from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import GoalAddAmountForm, GoalForm, SignUpForm, TransactionForm
from .models import Category, Goal, Transaction
from .services import expenses_by_category_qs, monthly_balance_qs


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("finance:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Category.objects.bulk_create(
                [
                    Category(user=user, name="Зарплата", is_income=True),
                    Category(user=user, name="Еда", is_income=False),
                    Category(user=user, name="Транспорт", is_income=False),
                    Category(user=user, name="Развлечения", is_income=False),
                    Category(user=user, name="Переводы", is_income=False),
                    Category(user=user, name="Бытовые нужды", is_income=False),
                ]
            )
            login(request, user)
            return redirect("finance:dashboard")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard_view(request):
    user = request.user

    date_from_str = request.GET.get("date_from")
    date_to_str = request.GET.get("date_to")
    tx_type = request.GET.get("type")
    category_id = request.GET.get("category")

    today = datetime.today().date()
    default_from = today.replace(day=1)
    default_to = today

    try:
        date_from = (
            datetime.strptime(date_from_str, "%Y-%m-%d").date()
            if date_from_str
            else default_from
        )
    except ValueError:
        date_from = default_from

    try:
        date_to = (
            datetime.strptime(date_to_str, "%Y-%m-%d").date()
            if date_to_str
            else default_to
        )
    except ValueError:
        date_to = default_to

    transactions_qs = Transaction.objects.filter(
        user=user,
        date__gte=date_from,
        date__lte=date_to,
    )

    if tx_type in ("income", "expense"):
        transactions_qs = transactions_qs.filter(type=tx_type)

    if category_id and category_id.isdigit():
        transactions_qs = transactions_qs.filter(category_id=int(category_id))

    transactions = transactions_qs.order_by("-date", "-id")[:5]

    income_sum = (
        Transaction.objects.filter(
            user=user,
            date__gte=date_from,
            date__lte=date_to,
            type="income",
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    expense_sum = (
        Transaction.objects.filter(
            user=user,
            date__gte=date_from,
            date__lte=date_to,
            type="expense",
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
    balance = income_sum - expense_sum

    agg = (
        transactions_qs.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    chart_labels = []
    chart_data = []
    for row in agg:
        label = row["category__name"] or "Без категории"
        chart_labels.append(label)
        chart_data.append(float(row["total"]))

    user_categories = Category.objects.filter(user=user).order_by("name")

    goals = Goal.objects.filter(user=user).order_by("-created_at")[:3]

    context = {
        "transactions": transactions,
        "income_sum": income_sum,
        "expense_sum": expense_sum,
        "balance": balance,
        "goals": goals,
        "date_from": date_from,
        "date_to": date_to,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "categories": user_categories,
        "selected_type": tx_type or "",
        "selected_category_id": int(category_id)
        if (category_id and category_id.isdigit())
        else "",
    }
    return render(request, "finance/dashboard.html", context)


@login_required
def transactions_list_view(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, "finance/transactions_list.html", {"transactions": transactions})


@login_required
@require_http_methods(["GET", "POST"])
def transaction_create_view(request):
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect("finance:transactions_list")
    else:
        form = TransactionForm(user=request.user)
    return render(request, "finance/transaction_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def transaction_update_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(
            request.POST,
            instance=transaction,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            return redirect("finance:transactions_list")
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    return render(request, "finance/transaction_form.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def transaction_delete_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    return redirect("finance:transactions_list")


@login_required
def goals_list_view(request):
    goals = Goal.objects.filter(user=request.user)
    return render(request, "finance/goals_list.html", {"goals": goals})


@login_required
@require_http_methods(["GET", "POST"])
def goal_create_view(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("finance:goals_list")
    else:
        form = GoalForm()
    return render(request, "finance/goal_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def goal_update_view(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    completed_before = goal.is_completed
    if request.method == "POST":
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save()
            completed_after = goal.is_completed
            message = None
            if not completed_before and completed_after:
                message = "Ваша цель достигнута, вы можете воплотить её!"
            return render(
                request,
                "finance/goal_form.html",
                {"form": form, "goal": goal, "success_message": message},
            )
    else:
        form = GoalForm(instance=goal)
    return render(request, "finance/goal_form.html", {"form": form, "goal": goal})


@login_required
@require_http_methods(["POST"])
def goal_delete_view(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    return redirect("finance:goals_list")


@login_required
def analytics_view(request):
    user = request.user

    year_str = request.GET.get("year")
    selected_year = None
    if year_str and year_str.isdigit():
        selected_year = int(year_str)

    from .services import expenses_by_category_qs, monthly_balance_qs, available_years_qs

    by_cat = expenses_by_category_qs(user)
    by_month = monthly_balance_qs(user, year=selected_year)

    if by_cat["labels"] and by_cat["data"]:
        max_value = max(by_cat["data"])
        max_index = by_cat["data"].index(max_value)
        main_category = by_cat["labels"][max_index]
    else:
        main_category = None

    years = available_years_qs(user)

    return render(
        request,
        "finance/analytics.html",
        {
            "by_cat": by_cat,
            "by_month": by_month,
            "main_category": main_category,
            "years": years,
            "selected_year": selected_year,
        },
    )


@login_required
@require_http_methods(["POST"])
def goal_add_amount_view(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)

    if goal.is_completed:
        return redirect("finance:goals_list")

    form = GoalAddAmountForm(request.POST)
    if form.is_valid():
        amount = form.cleaned_data["amount"]
        goal.current_amount = goal.current_amount + amount
        goal.save()
    return redirect("finance:goals_list")

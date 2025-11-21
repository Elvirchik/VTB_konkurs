from typing import Dict, Any, Optional
import pandas as pd

from .models import Transaction


def expenses_by_category_qs(user) -> Dict[str, Any]:
    qs = Transaction.objects.filter(user=user, type="expense")
    if not qs.exists():
        return {"labels": [], "data": []}

    df = pd.DataFrame.from_records(
        qs.values("category__name", "amount"),
        columns=["category__name", "amount"],
    )
    df = df.groupby("category__name")["amount"].sum().reset_index()
    labels = df["category__name"].fillna("Без категории").tolist()
    data = [float(x) for x in df["amount"].tolist()]
    return {"labels": labels, "data": data}


def monthly_balance_qs(user, year: Optional[int] = None) -> Dict[str, Any]:
    qs = Transaction.objects.filter(user=user)
    if year is not None:
        qs = qs.filter(date__year=year)  # фильтрация по году [web:159][web:168]

    if not qs.exists():
        return {"labels": [], "income": [], "expense": []}

    df = pd.DataFrame.from_records(qs.values("date", "type", "amount"))
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    pivot = df.pivot_table(
        index="month",
        columns="type",
        values="amount",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    labels = pivot["month"].tolist()
    income_series = pivot.get("income")
    expense_series = pivot.get("expense")

    income = [float(x) for x in (income_series.tolist() if income_series is not None else [0] * len(labels))]
    expense = [float(x) for x in (expense_series.tolist() if expense_series is not None else [0] * len(labels))]

    return {"labels": labels, "income": income, "expense": expense}


def available_years_qs(user) -> list[int]:
    """
    Список годов, в которых есть какие-либо операции пользователя,
    чтобы заполнить селект в аналитике.
    """
    qs = Transaction.objects.filter(user=user)
    if not qs.exists():
        return []
    df = pd.DataFrame.from_records(qs.values("date"))
    years = sorted(df["date"].apply(lambda d: d.year).unique())
    return [int(y) for y in years]

from datetime import date, timedelta
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Transaction, Goal, Category


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Укажите действующий адрес электронной почты.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "category", "amount", "date", "description"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["amount"].help_text = "Введите положительную сумму операции."
        self.fields["date"].help_text = "Дата операции не может быть в будущем."
        self.fields["description"].help_text = "Кратко опишите операцию (необязательно)."
        # Ограничиваем категории только теми, которые принадлежат текущему пользователю
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user)
        # Добавляем стили CSS и атрибуты в поля формы для удобства отображения и валидации
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            if name in ("type", "category"):
                field.widget.attrs["class"] = (css + " form-select").strip()
            elif name == "amount":
                field.widget.attrs["class"] = (css + " form-control").strip()
                field.widget.attrs["min"] = "0.01"
                if isinstance(field, forms.DecimalField):
                    field.min_value = Decimal("0.01")
            elif name == "date":
                field.widget.attrs["class"] = (css + " form-control").strip()
                field.widget.attrs["max"] = date.today().isoformat()
            else:
                field.widget.attrs["class"] = (css + " form-control").strip()

    # Валидация поля amount — сумма должна быть больше 0
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            return amount
        if amount <= Decimal("0.00"):
            raise forms.ValidationError("Сумма операции должна быть больше нуля.")
        return amount

    # Валидация поля date — дата не должна быть в будущем
    def clean_date(self):
        d = self.cleaned_data.get("date")
        if d is None:
            return d
        today = date.today()
        if d > today:
            raise forms.ValidationError(
                "Дата операции не может быть в будущем. Укажите сегодняшнюю или прошедшую дату."
            )
        return d


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["name", "target_amount", "current_amount", "deadline"]
        widgets = {
            "deadline": forms.DateInput(
                attrs={
                    "type": "date",
                }# виджет выбора даты
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].help_text = "Например: подушка безопасности, отпуск, новый телефон."
        self.fields["target_amount"].help_text = "Сколько хотите накопить по этой цели."
        self.fields["current_amount"].help_text = "Сколько уже накоплено по цели."
        self.fields["deadline"].help_text = "Укажите дату в будущем (начиная с завтрашнего дня)."
        # Добавляем CSS классы для стилизации полей
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()
        # Устанавливаем минимальное значение для target_amount и current_amount
        if isinstance(self.fields["target_amount"], forms.DecimalField):
            self.fields["target_amount"].min_value = Decimal("0.01")
            self.fields["target_amount"].widget.attrs["min"] = "0.01"
        if isinstance(self.fields["current_amount"], forms.DecimalField):
            self.fields["current_amount"].min_value = Decimal("0.00")
            self.fields["current_amount"].widget.attrs["min"] = "0.00"

        tomorrow = date.today() + timedelta(days=1)
        self.fields["deadline"].widget.attrs["min"] = tomorrow.isoformat()

    def clean_deadline(self):
        d = self.cleaned_data.get("deadline")
        if d is None:
            return d

        today = date.today()
        if d <= today:
            raise forms.ValidationError(
                "Дедлайн цели должен быть в будущем. Укажите дату, начиная с завтрашнего дня."
            )
        return d

    # Валидация целевой суммы - должна быть больше нуля
    def clean_target_amount(self):
        value = self.cleaned_data.get("target_amount")
        if value is None:
            return value
        if value <= Decimal("0.00"):
            raise forms.ValidationError("Целевая сумма должна быть больше нуля.")
        return value

    # Валидация текущей суммы — не может быть отрицательной
    def clean_current_amount(self):
        value = self.cleaned_data.get("current_amount")
        if value is None:
            return value
        if value < Decimal("0.00"):
            raise forms.ValidationError("Текущая сумма не может быть отрицательной.")
        return value

# Поле для добавления суммы к цели с минимальным значением
class GoalAddAmountForm(forms.Form):
    amount = forms.DecimalField(
        label="Добавить сумму",
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Введите сумму, которую хотите добавить к цели.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs["class"] = "form-control"
        self.fields["amount"].widget.attrs["min"] = "0.01"

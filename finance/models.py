from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Пользователь",
    )
    name = models.CharField(
        "Название категории",
        max_length=100,
    )
    is_income = models.BooleanField(
        "Это доходная категория",
        default=False,
    )

    class Meta:
        unique_together = ("user", "name")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):
    TYPE_CHOICES = (
        ("income", "Доход"),
        ("expense", "Расход"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Пользователь",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
    )
    type = models.CharField(
        "Тип операции",
        max_length=7,
        choices=TYPE_CHOICES,
    )
    amount = models.DecimalField(
        "Сумма",
        max_digits=12,
        decimal_places=2,
    )
    date = models.DateField(
        "Дата",
        default=timezone.now,
    )
    description = models.CharField(
        "Описание",
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Операция"
        verbose_name_plural = "Операции"

    def __str__(self) -> str:
        return f"{self.get_type_display()} {self.amount}"


class Goal(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="goals",
        verbose_name="Пользователь",
    )
    name = models.CharField(
        "Название цели",
        max_length=150,
    )
    target_amount = models.DecimalField(
        "Целевая сумма",
        max_digits=12,
        decimal_places=2,
    )
    current_amount = models.DecimalField(
        "Текущая сумма",
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    deadline = models.DateField(
        "Дедлайн",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Финансовая цель"
        verbose_name_plural = "Финансовые цели"

    @property
    def is_completed(self) -> bool:
        return self.current_amount >= self.target_amount

    @property
    def progress_percent(self) -> float:
        if not self.target_amount or self.target_amount == 0:
            return 0.0
        return float((self.current_amount / self.target_amount) * Decimal("100"))

    def __str__(self) -> str:
        return self.name

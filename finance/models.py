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
    ) # Название категории (например, "Еда" или "Зарплата")
    name = models.CharField(
        "Название категории",
        max_length=100,
    )# Флаг, указывающий, является ли категория доходной
    is_income = models.BooleanField(
        "Это доходная категория",
        default=False,
    )

    class Meta:
        # Уникальность категории для пользователя: одна категория
        # с таким именем может быть только у одного пользователя
        unique_together = ("user", "name")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    # Отображение категории в виде строки — выводится название категории
    def __str__(self) -> str:
        return self.name

# Выбор типа операции — доход или расход
class Transaction(models.Model):
    TYPE_CHOICES = (
        ("income", "Доход"),
        ("expense", "Расход"),
    )
    # Связь транзакции с пользователем
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Пользователь",
    )# Категория транзакции (может быть пустой)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
    )  # Тип операции: доход или расход
    type = models.CharField(
        "Тип операции",
        max_length=7,
        choices=TYPE_CHOICES,
    )
    amount = models.DecimalField(
        "Сумма",
        max_digits=12,
        decimal_places=2,
    )# Дата операции (по умолчанию — текущая дата)
    date = models.DateField(
        "Дата",
        default=timezone.now,
    )# Дополнительное описание операции, не обязательно
    description = models.CharField(
        "Описание",
        max_length=255,
        blank=True,
    )

    # Сортировка операций по дате и id (последние показываются первыми)
    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Операция"
        verbose_name_plural = "Операции"

    # Отображение операции строкой с типом и суммой
    def __str__(self) -> str:
        return f"{self.get_type_display()} {self.amount}"

# Связь цели с пользователем
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

    # Свойство, которое возвращает True, если цель достигнута (накоплено достаточно денег)
    @property
    def is_completed(self) -> bool:
        return self.current_amount >= self.target_amount

    # Свойство для вычисления процента выполнения цели (от 0 до 100)
    @property
    def progress_percent(self) -> float:
        if not self.target_amount or self.target_amount == 0:
            return 0.0
        return float((self.current_amount / self.target_amount) * Decimal("100"))

    # Отображение цели строкой — выводится её название
    def __str__(self) -> str:
        return self.name

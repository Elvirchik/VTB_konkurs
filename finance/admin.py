from django.contrib import admin
from .models import Category, Transaction, Goal


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "is_income")
    list_filter = ("is_income", "user")
    search_fields = ("name", "user__username")
    list_display_links = ("id", "name")
    ordering = ("user", "name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
        "category",
        "amount",
        "date",
        "description_short",
    )
    list_filter = ("type", "category", "date", "user")
    search_fields = ("description", "user__username", "category__name")
    list_display_links = ("id", "description_short")
    date_hierarchy = "date"
    ordering = ("-date", "-id")

    def description_short(self, obj):
        if not obj.description:
            return "-"
        if len(obj.description) > 40:
            return obj.description[:37] + "..."
        return obj.description

    description_short.short_description = "Описание"


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "target_amount",
        "current_amount",
        "progress_percent_display",
        "deadline",
        "created_at",
        "is_completed",
    )
    list_filter = ("user", "deadline", "created_at")
    search_fields = ("name", "user__username")
    list_display_links = ("id", "name")
    ordering = ("-created_at",)

    readonly_fields = ("progress_percent_display", "is_completed")

    fieldsets = (
        (None, {
            "fields": ("user", "name"),
        }),
        ("Суммы", {
            "fields": ("target_amount", "current_amount", "progress_percent_display"),
        }),
        ("Даты", {
            "fields": ("deadline", "created_at", "is_completed"),
        }),
    )

    def progress_percent_display(self, obj):
        return f"{obj.progress_percent:.1f}%"

    progress_percent_display.short_description = "Прогресс"

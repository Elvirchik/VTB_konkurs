from django.urls import path
from . import views

urlpatterns = [
    # Корневой URL ('') связывается с функцией dashboard_view, которая отображает главную панель пользователя
    path("", views.dashboard_view, name="dashboard"),

    # URL для регистрации нового пользователя, вызывает функцию signup_view
    path("signup/", views.signup_view, name="signup"),

    # Отображение списка всех транзакций пользователя через функцию transactions_list_view
    path("transactions/", views.transactions_list_view, name="transactions_list"),

    # URL для добавления новой транзакции, вызывает transaction_create_view
    path("transactions/add/", views.transaction_create_view, name="transaction_create"),

    # Редактирование транзакции, параметр pk (primary key) определяет конкретную транзакцию
    path("transactions/<int:pk>/edit/", views.transaction_update_view, name="transaction_update"),

    # Удаление транзакции по ее pk
    path("transactions/<int:pk>/delete/", views.transaction_delete_view, name="transaction_delete"),

    # Отображение списка целей пользователя (цели накоплений и т.д.)
    path("goals/", views.goals_list_view, name="goals_list"),

    # Добавление новой цели
    path("goals/add/", views.goal_create_view, name="goal_create"),

    # Редактирование существующей цели через pk
    path("goals/<int:pk>/edit/", views.goal_update_view, name="goal_update"),

    # Удаление цели по pk
    path("goals/<int:pk>/delete/", views.goal_delete_view, name="goal_delete"),

    # Добавление суммы к уже существующей цели (например, внесение денег)
    path("goals/<int:pk>/add_amount/", views.goal_add_amount_view, name="goal_add_amount"),

    # Просмотр аналитики финансов (графики, отчеты)
    path("analytics/", views.analytics_view, name="analytics"),
]

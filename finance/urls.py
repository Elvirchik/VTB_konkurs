from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("signup/", views.signup_view, name="signup"),

    path("transactions/", views.transactions_list_view, name="transactions_list"),
    path("transactions/add/", views.transaction_create_view, name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.transaction_update_view, name="transaction_update"),
    path("transactions/<int:pk>/delete/", views.transaction_delete_view, name="transaction_delete"),

    path("goals/", views.goals_list_view, name="goals_list"),
    path("goals/add/", views.goal_create_view, name="goal_create"),
    path("goals/<int:pk>/edit/", views.goal_update_view, name="goal_update"),
    path("goals/<int:pk>/delete/", views.goal_delete_view, name="goal_delete"),

    path("goals/<int:pk>/add_amount/", views.goal_add_amount_view, name="goal_add_amount"),

    path("analytics/", views.analytics_view, name="analytics"),
]

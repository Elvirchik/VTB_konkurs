from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("finance/", include(("finance.urls", "finance"), namespace="finance")),
    path("", RedirectView.as_view(pattern_name="finance:dashboard", permanent=False)),
]

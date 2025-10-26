from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # inclui o app core
    path("", RedirectView.as_view(pattern_name="portaria_busca", permanent=False)),
]


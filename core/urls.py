# core/urls.py
from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path("portaria/", views.portaria_busca, name="portaria_busca"),
    path("", RedirectView.as_view(pattern_name="portaria_busca", permanent=False)),
]

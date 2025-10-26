from django.urls import path
from . import views

urlpatterns = [
    path("portaria/", views.portaria_busca, name="portaria_busca"),
]

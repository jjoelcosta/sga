from django.urls import path
from . import views

urlpatterns = [
    # Deixa a home e /portaria apontando pra mesma view que já existe
    path("", views.portaria_busca, name="portaria_busca"),
    path("portaria/", views.portaria_busca, name="portaria_busca"),
]

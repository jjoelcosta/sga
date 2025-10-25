from django.urls import path
from .views import portaria_busca

urlpatterns = [
    path("portaria/", portaria_busca, name="portaria"),
]
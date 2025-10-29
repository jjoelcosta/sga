# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Raiz serve a tela de busca diretamente, sem RedirectView
    path("", views.portaria_busca, name="portaria_busca"),

    # Cadastros
    path("cadastro/", views.cadastro_home, name="cadastro_home"),
    path("cadastro/empresa/", views.empresa_criar, name="empresa_criar"),
    path("cadastro/colaborador/", views.colaborador_criar, name="colaborador_criar"),
    path("cadastro/veiculo/", views.veiculo_criar, name="veiculo_criar"),
    path("cadastro/acesso/", views.acesso_criar, name="acesso_criar"),

    # Upload em lote
    path("upload/", views.upload_lotes, name="upload_lotes"),

    # Listagens
    path("lista/empresas/", views.empresa_listar, name="empresa_listar"),
    path("lista/colaboradores/", views.colaborador_listar, name="colaborador_listar"),
    path("lista/veiculos/", views.veiculo_listar, name="veiculo_listar"),

]
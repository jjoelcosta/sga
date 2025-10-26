from django.contrib import admin
from .models import Empresa, Colaborador, Veiculo, Atribuicao


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "responsavel", "telefone")
    search_fields = ("nome", "cnpj", "responsavel")
    list_per_page = 25


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "funcao", "empresa")
    search_fields = ("nome", "cpf", "funcao", "empresa__nome")
    list_filter = ("empresa",)
    autocomplete_fields = ("empresa",)


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "cor", "colaborador")
    search_fields = ("placa", "marca", "modelo", "colaborador__nome")
    list_filter = ("marca", "cor")
    autocomplete_fields = ("colaborador",)


@admin.register(Atribuicao)
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "veiculo", "local", "data_inicio", "data_fim", "status")
    list_filter = ("status", "local", "data_inicio", "data_fim")
    search_fields = ("colaborador__nome", "veiculo__placa", "colaborador__empresa__nome")
    date_hierarchy = "data_inicio"
    autocomplete_fields = ("colaborador", "veiculo")


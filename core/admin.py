from django.contrib import admin
from .models import Empresa, Colaborador, Veiculo, Atribuicao  # ajuste aqui se for "Acesso" em vez de "Atribuicao"

# -------- Empresa --------
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "responsavel")  # removido 'email'
    search_fields = ("nome", "cnpj", "responsavel")  # se existir email no futuro, pode incluir aqui

    # Removemos list_filter de campos inexistentes (ex: ramo_atividade)

# -------- Colaborador --------
@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "empresa", "funcao")  # removido "telefone"
    search_fields = ("nome", "cpf")
    list_filter = ("empresa",)  # filtra por FK existente
    autocomplete_fields = ("empresa",)

# -------- Veiculo --------
@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "cor", "colaborador", "get_empresa")
    search_fields = ("placa", "marca", "modelo", "cor", "colaborador__nome", "colaborador__empresa__nome")
    list_filter = ("marca", "cor")  # removido "tipo" (não existe)
    autocomplete_fields = ("colaborador",)

    @admin.display(description="Empresa")
    def get_empresa(self, obj):
        try:
            return obj.colaborador.empresa
        except Exception:
            return "—"

# -------- Atribuicao (ou Acesso) --------
@admin.register(Atribuicao)  # Se seu modelo chama "Acesso", troque o nome aqui e na import no topo
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "get_empresa", "veiculo", "local", "data_inicio", "data_fim", "status")
    search_fields = ("colaborador__nome", "colaborador__cpf", "veiculo__placa", "local")
    list_filter = ("status", "local", "data_inicio", "data_fim")
    autocomplete_fields = ("colaborador", "veiculo")

    @admin.display(description="Empresa")
    def get_empresa(self, obj):
        try:
            return obj.colaborador.empresa
        except Exception:
            return "—"


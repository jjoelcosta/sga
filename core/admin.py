from django.contrib import admin
from .models import Empresa, Colaborador, Veiculo, Atribuicao, LoteImportacao, Acesso


@admin.register(LoteImportacao)
class LoteImportacaoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "arquivo_nome", "criado_em", "ok", "total_processado", "total_erros", "relatorio_curto")
    list_filter = ("tipo", "ok", "criado_em")
    search_fields = ("arquivo_nome",)
    readonly_fields = ("criado_em", "ok", "total_processado", "total_erros", "log")
    ordering = ("-criado_em",)

    def relatorio_curto(self, obj):
        """
        Exibe um resumo curto do log (se JSON) ou primeiros 200 chars do texto.
        """
        try:
            if isinstance(obj.log, dict):
                # tenta mostrar um resumo simples: total de erros e primeiras chaves
                erros = obj.log.get("erros", None)
                if erros:
                    return f"Erros: {len(erros)}"
                return "OK"
            return (obj.log or "")[:200]
        except Exception:
            return "—"
    relatorio_curto.short_description = "Relatório"


# -------- Empresa --------
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "responsavel")
    search_fields = ("nome", "cnpj", "responsavel")
    readonly_fields = ()
    ordering = ("nome",)


# -------- Colaborador --------
@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "empresa", "funcao")
    search_fields = ("nome", "cpf")
    list_filter = ("empresa",)
    autocomplete_fields = ("empresa",)
    ordering = ("nome",)


# -------- Veiculo --------
@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "cor", "colaborador", "get_empresa")
    search_fields = ("placa", "marca", "modelo", "cor", "colaborador__nome", "colaborador__empresa__nome")
    list_filter = ("marca", "cor")
    autocomplete_fields = ("colaborador",)
    ordering = ("placa",)

    @admin.display(description="Empresa")
    def get_empresa(self, obj):
        try:
            return obj.colaborador.empresa
        except Exception:
            return "—"


# -------- Atribuicao (ou Acesso) --------
@admin.register(Atribuicao)
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "get_empresa", "veiculo", "local", "data_inicio", "data_fim", "status")
    search_fields = ("colaborador__nome", "colaborador__cpf", "veiculo__placa", "local")
    list_filter = ("status", "local", "data_inicio", "data_fim")
    autocomplete_fields = ("colaborador", "veiculo")
    ordering = ("-data_inicio",)

    @admin.display(description="Empresa")
    def get_empresa(self, obj):
        try:
            return obj.colaborador.empresa
        except Exception:
            return "—"


# -------- Acesso (auditoria de liberações) --------
@admin.register(Acesso)
class AcessoAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "get_empresa", "veiculo", "local", "data_inicio", "data_fim", "status", "criado_por", "ip_address")
    search_fields = ("colaborador__nome", "colaborador__cpf", "veiculo__placa", "local", "criado_por__username")
    list_filter = ("status", "local", "data_inicio")
    readonly_fields = ("created_at", "updated_at", "criado_por", "ip_address", "dispositivo")
    autocomplete_fields = ("colaborador", "veiculo", "criado_por")
    ordering = ("-data_inicio",)

    @admin.display(description="Empresa")
    def get_empresa(self, obj):
        try:
            return obj.colaborador.empresa
        except Exception:
            return "—"
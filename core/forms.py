from django import forms
from .models import Empresa, Colaborador, Veiculo, Acesso
import re

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["cnpj", "nome", "responsavel", "telefone"]

    def clean_cnpj(self):
        cnpj = re.sub(r"\D", "", self.cleaned_data.get("cnpj", ""))
        if len(cnpj) != 14:
            raise forms.ValidationError("CNPJ deve ter 14 dígitos.")
        return cnpj


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["cpf", "nome", "funcao", "empresa"]

    def clean_cpf(self):
        cpf = re.sub(r"\D", "", self.cleaned_data.get("cpf", ""))
        if len(cpf) != 11:
            raise forms.ValidationError("CPF deve ter 11 dígitos.")
        return cpf


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ["placa", "marca", "modelo", "cor", "colaborador"]

    def clean_placa(self):
        placa = re.sub(r"[^A-Za-z0-9]", "", self.cleaned_data.get("placa", "")).upper()
        if not (7 <= len(placa) <= 8):
            raise forms.ValidationError("Placa deve ter 7 ou 8 caracteres.")
        return placa


class AcessoForm(forms.ModelForm):
    class Meta:
        model = Acesso
        fields = ["colaborador", "veiculo", "local", "data_inicio", "data_fim", "status", "observacao"]


class UploadArquivoForm(forms.Form):
    TIPO_CHOICES = [
        ("empresa", "Empresas"),
        ("colaborador", "Colaboradores"),
        ("veiculo", "Veículos"),
        ("atribuicao", "Atribuições"),
    ]
    tipo = forms.ChoiceField(choices=TIPO_CHOICES)
    arquivo = forms.FileField(help_text="CSV ou XLSX")
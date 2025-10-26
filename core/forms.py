from django import forms
from .models import Empresa, Colaborador, Veiculo, Atribuicao
import re

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nome", "cnpj"]
        widgets = {
            "nome": forms.TextInput(attrs={"class":"form-control"}),
            "cnpj": forms.TextInput(attrs={"class":"form-control", "placeholder":"Apenas números"}),
        }
    def clean_cnpj(self):
        cnpj = re.sub(r"\D+","", self.cleaned_data.get("cnpj",""))
        if len(cnpj) != 14:
            raise forms.ValidationError("CNPJ deve ter 14 dígitos.")
        return cnpj

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["nome", "cpf", "empresa", "funcao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class":"form-control"}),
            "cpf": forms.TextInput(attrs={"class":"form-control", "placeholder":"Apenas números"}),
            "empresa": forms.Select(attrs={"class":"form-select"}),
            "funcao": forms.TextInput(attrs={"class":"form-control"}),
        }
    def clean_cpf(self):
        cpf = re.sub(r"\D+","", self.cleaned_data.get("cpf",""))
        if len(cpf) != 11:
            raise forms.ValidationError("CPF deve ter 11 dígitos.")
        return cpf

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ["placa", "colaborador"]
        widgets = {
            "placa": forms.TextInput(attrs={"class":"form-control", "placeholder":"ABC1D23"}),
            "colaborador": forms.Select(attrs={"class":"form-select"}),
        }
    def clean_placa(self):
        placa = re.sub(r"[^A-Za-z0-9]","", self.cleaned_data.get("placa","")).upper()
        if not (7 <= len(placa) <= 8):
            raise forms.ValidationError("Placa deve ter 7 ou 8 caracteres.")
        return placa

class AtribuicaoForm(forms.ModelForm):
    class Meta:
        model = Atribuicao
        fields = ["colaborador", "veiculo", "status", "local", "data_inicio", "data_fim"]
        widgets = {
            "colaborador": forms.Select(attrs={"class":"form-select"}),
            "veiculo": forms.Select(attrs={"class":"form-select"}),
            "status": forms.Select(attrs={"class":"form-select"}),
            "local": forms.TextInput(attrs={"class":"form-control"}),
            "data_inicio": forms.DateInput(attrs={"class":"form-control", "type":"date"}),
            "data_fim": forms.DateInput(attrs={"class":"form-control", "type":"date"}),
        }

class UploadPlanilhaForm(forms.Form):
    TIPO_CHOICES = (
        ("empresa","Empresas"),
        ("colaborador","Colaboradores"),
        ("veiculo","Veículos"),
        ("atribuicao","Atribuições"),
    )
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={"class":"form-select"}))
    arquivo = forms.FileField(widget=forms.ClearableFileInput(attrs={"class":"form-control"}))

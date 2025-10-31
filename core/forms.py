from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .models import Empresa, Colaborador, Veiculo, Acesso
import re


def _only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["cnpj", "nome", "responsavel", "telefone"]

    def clean_cnpj(self):
        cnpj = _only_digits(self.cleaned_data.get("cnpj", ""))
        if len(cnpj) != 14:
            raise forms.ValidationError("CNPJ deve ter 14 dígitos (somente números).")
        return cnpj


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["cpf", "nome", "funcao", "empresa"]

    def clean_cpf(self):
        cpf = _only_digits(self.cleaned_data.get("cpf", ""))
        if len(cpf) != 11:
            raise forms.ValidationError("CPF deve ter 11 dígitos (somente números).")
        return cpf


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ["placa", "marca", "modelo", "cor", "colaborador"]

    def clean_placa(self):
        placa_raw = self.cleaned_data.get("placa", "") or ""
        placa = re.sub(r"[^A-Za-z0-9]", "", placa_raw).upper()
        # placas brasileiras atuais têm 7 caracteres; alguns sistemas usam 8 (ex.: mercosul com hífen removido)
        if not (7 <= len(placa) <= 8):
            raise forms.ValidationError("Placa deve ter 7 ou 8 caracteres alfanuméricos.")
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
    arquivo = forms.FileField(
        help_text="CSV ou XLSX",
        validators=[FileExtensionValidator(allowed_extensions=["csv", "xlsx"])],
    )

    def clean_arquivo(self):
        f = self.cleaned_data["arquivo"]
        name = f.name.lower()

        # Verifica extensão via validator acima; aqui só reforçamos o tamanho/segurança
        max_size = getattr(settings, "MAX_UPLOAD_SIZE", 5 * 1024 * 1024)  # 5 MB por padrão
        if f.size > max_size:
            raise forms.ValidationError(f"O arquivo deve ter no máximo {max_size // (1024 * 1024)} MB.")

        # Não confiar unicamente no content_type: alguns navegadores mudam o valor.
        # Se for necessário maior robustez, inspecione o cabeçalho inicial (magic bytes) aqui.
        return f
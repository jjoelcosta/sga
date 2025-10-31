from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

cpf_validator = RegexValidator(r"^\d{11}$", "CPF deve conter 11 dígitos numéricos (sem pontuação).")
cnpj_validator = RegexValidator(r"^\d{14}$", "CNPJ deve conter 14 dígitos numéricos (sem pontuação).")
placa_validator = RegexValidator(r"^[A-Z0-9]{7,8}$", "Placa inválida (7 ou 8 caracteres alfanuméricos, sem pontuação).")


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Empresa(TimestampedModel):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=14, unique=True, validators=[cnpj_validator])
    responsavel = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome"]
        indexes = [models.Index(fields=["cnpj"])]


class Colaborador(TimestampedModel):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True, validators=[cpf_validator])
    funcao = models.CharField(max_length=100, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="colaboradores")

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"

    class Meta:
        ordering = ["nome"]
        indexes = [models.Index(fields=["cpf"]), models.Index(fields=["empresa"])]


class Veiculo(TimestampedModel):
    colaborador = models.ForeignKey(
        Colaborador, on_delete=models.SET_NULL, null=True, blank=True, related_name="veiculos"
    )
    placa = models.CharField(max_length=10, unique=True, validators=[placa_validator])
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    cor = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.placa

    class Meta:
        indexes = [models.Index(fields=["placa"])]


class Atribuicao(TimestampedModel):
    STATUS_LIBERADO = "LIBERADO"
    STATUS_PENDENTE = "PENDENTE"
    STATUS_BLOQUEADO = "BLOQUEADO"
    STATUS_CHOICES = [
        (STATUS_LIBERADO, "Liberado"),
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_BLOQUEADO, "Bloqueado"),
    ]

    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name="atribuicoes")
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True)
    local = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDENTE)

    def __str__(self):
        return f"{self.colaborador.nome} - {self.local}"

    def is_active(self, when=None):
        when = when or timezone.now().date()
        return self.data_inicio <= when <= (self.data_fim or when) and self.status == self.STATUS_LIBERADO

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.data_inicio and self.data_fim and self.data_inicio > self.data_fim:
            raise ValidationError("data_inicio não pode ser posterior a data_fim")

    class Meta:
        indexes = [models.Index(fields=["colaborador", "local"]), models.Index(fields=["status"])]


class Acesso(TimestampedModel):
    STATUS_LIBERADO = "LIBERADO"
    STATUS_BLOQUEADO = "BLOQUEADO"
    STATUS_PENDENTE = "PENDENTE"
    STATUS_CHOICES = [
        (STATUS_LIBERADO, "Liberado"),
        (STATUS_BLOQUEADO, "Bloqueado"),
        (STATUS_PENDENTE, "Pendente"),
    ]

    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name="acessos")
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True)
    local = models.CharField(max_length=100)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    observacao = models.TextField(blank=True, null=True)

    # Auditoria: quem realizou a ação, dispositivo e IP (preenchidos pela view/middleware)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="acessos_criados")
    dispositivo = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.colaborador.nome} - {self.status} - {self.local}"

    class Meta:
        indexes = [models.Index(fields=["colaborador", "local", "status", "data_inicio"])]


class LoteImportacao(TimestampedModel):
    TIPOS = [
        ("empresa", "Empresas"),
        ("colaborador", "Colaboradores"),
        ("veiculo", "Veículos"),
        ("atribuicao", "Atribuições"),
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS)
    arquivo_nome = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)
    ok = models.BooleanField(default=False)
    total_processado = models.IntegerField(default=0)
    total_erros = models.IntegerField(default=0)
    # Armazena relatório/erros estruturados; JSONField é compatível com SQLite e Postgres em Django 3.1+
    log = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} • {self.arquivo_nome} • {self.criado_em:%d/%m/%Y %H:%M}"

    class Meta:
        ordering = ["-criado_em"]
        indexes = [models.Index(fields=["tipo", "criado_em"])]

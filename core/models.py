from django.db import models


class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    responsavel = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome


class Colaborador(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    funcao = models.CharField(max_length=100, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='colaboradores')

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome})"


class Veiculo(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, blank=True)
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    cor = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.placa


class Atribuicao(models.Model):
    STATUS_CHOICES = [
        ('LIBERADO', 'Liberado'),
        ('PENDENTE', 'Pendente'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True)
    local = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')

    def __str__(self):
        return f"{self.colaborador.nome} - {self.local}"
    
class Acesso(models.Model):
    colaborador = models.ForeignKey("Colaborador", on_delete=models.CASCADE)
    veiculo = models.ForeignKey("Veiculo", on_delete=models.SET_NULL, null=True, blank=True)
    local = models.CharField(max_length=100)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("LIBERADO", "Liberado"),
            ("BLOQUEADO", "Bloqueado"),
            ("PENDENTE", "Pendente"),
        ],
        default="PENDENTE",
    )
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.colaborador.nome} - {self.status}"    

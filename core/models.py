from django.db import models

from django.db import models

class Empresa(models.Model):
    nome = models.CharField(max_length=200, unique=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)

    def __str__(self):
        return self.nome

class Colaborador(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='colaboradores')
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)

    def __str__(self):
        return self.nome

class Veiculo(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='veiculos')
    placa = models.CharField(max_length=10)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    cor = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.placa

class Acesso(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='acessos')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    liberado = models.BooleanField(default=False)
    atribuicao_local = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.colaborador} ({self.data_inicio} - {self.data_fim})'


from django.contrib import admin
from .models import Empresa, Colaborador, Veiculo, Acesso

admin.site.register(Empresa)
admin.site.register(Colaborador)
admin.site.register(Veiculo)
admin.site.register(Acesso)

from django.shortcuts import render
from .models import Acesso

def portaria_busca(request):
    termo = request.GET.get("q", "")
    resultados = []

    if termo:
        resultados = Acesso.objects.filter(colaborador__nome__icontains=termo)

    return render(request, "core/portaria_busca.html", {"termo": termo, "resultados": resultados})


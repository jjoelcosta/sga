# core/views.py
from django.shortcuts import render
from django.db.models import Q
from datetime import date
import re

from .models import Atribuicao  # <- seu modelo de autorizações
# se precisar: from .models import Colaborador, Veiculo, Empresa

def _limpa_cpf(termo: str):
    if not termo:
        return None
    digits = re.sub(r"\D+", "", termo)
    return digits if len(digits) == 11 else None

def _limpa_placa(termo: str):
    if not termo:
        return None
    placa = re.sub(r"[^A-Za-z0-9]", "", termo).upper()
    return placa if 7 <= len(placa) <= 8 else None

def portaria_busca(request):
    termo = request.GET.get("q", "").strip()
    resultados = []

    if termo:
        hoje = date.today()
        cpf = _limpa_cpf(termo)
        placa = _limpa_placa(termo)

        qs = (Atribuicao.objects
              .select_related("colaborador", "veiculo", "colaborador__empresa"))

        if placa:
            qs = qs.filter(veiculo__placa=placa)
        elif cpf:
            qs = qs.filter(colaborador__cpf=cpf)
        else:
            qs = qs.filter(
                Q(colaborador__nome__icontains=termo) |
                Q(colaborador__empresa__nome__icontains=termo)
            )

        for a in qs.order_by("-data_inicio")[:200]:
            dentro_janela = (a.data_inicio is None or a.data_inicio <= hoje) and \
                            (a.data_fim is None or a.data_fim >= hoje)

            if a.status == "LIBERADO" and dentro_janela:
                status_final = "LIBERADO"
            elif a.status == "BLOQUEADO":
                status_final = "BLOQUEADO"
            else:
                status_final = "PENDENTE"

            resultados.append({
                "status_final": status_final,
                "nome": a.colaborador.nome if a.colaborador else "—",
                "empresa": a.colaborador.empresa.nome if a.colaborador and a.colaborador.empresa else "—",
                "funcao": a.colaborador.funcao if a.colaborador and a.colaborador.funcao else "—",
                "placa": a.veiculo.placa if a.veiculo else None,
                "local": a.local or "—",
                "data_inicio": a.data_inicio,
                "data_fim": a.data_fim,
            })

    return render(request, "core/portaria_busca.html", {"termo": termo, "resultados": resultados})

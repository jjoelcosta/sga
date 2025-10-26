from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import date, datetime
from django.db.models import Q
import re

from .models import Colaborador, Veiculo, Atribuicao, Empresa

def _limpa_cpf(termo):
    digits = re.sub(r'\D+', '', termo or '')
    return digits if len(digits) == 11 else None

def _limpa_placa(termo):
    if not termo: return None
    placa = re.sub(r'[^A-Za-z0-9]', '', termo).upper()
    return placa if 7 <= len(placa) <= 8 else None

def portaria_busca(request):
    termo = request.GET.get('q', '').strip()
    somente_hoje = request.GET.get('somente_hoje', 'on')  # default ligado
    data_de = request.GET.get('data_de', '')
    data_ate = request.GET.get('data_ate', '')
    status = request.GET.get('status', '')  # '', LIBERADO, PENDENTE, BLOQUEADO

    resultados = []
    hoje = date.today()

    qs = Atribuicao.objects.select_related('colaborador', 'veiculo', 'colaborador__empresa')

    # Busca por termo (placa / cpf / nome / empresa)
    if termo:
        cpf = _limpa_cpf(termo)
        placa = _limpa_placa(termo)
        if placa:
            qs = qs.filter(veiculo__placa=placa)
        elif cpf:
            qs = qs.filter(colaborador__cpf=cpf)
        else:
            qs = qs.filter(
                Q(colaborador__nome__icontains=termo) |
                Q(colaborador__empresa__nome__icontains=termo)
            )

    # Filtro “somente hoje”
    if somente_hoje == 'on':
        qs = qs.filter(
            Q(data_inicio__isnull=True) | Q(data_inicio__lte=hoje),
            Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
        )
    else:
        # Filtro por período, se preenchido
        try:
            if data_de:
                d_de = datetime.strptime(data_de, "%Y-%m-%d").date()
                qs = qs.filter(data_fim__gte=d_de)
            if data_ate:
                d_ate = datetime.strptime(data_ate, "%Y-%m-%d").date()
                qs = qs.filter(data_inicio__lte=d_ate)
        except ValueError:
            pass  # se data vier malformada, ignora silenciosamente neste MVP

    # Filtro por status, se escolhido
    if status in ("LIBERADO", "PENDENTE", "BLOQUEADO"):
        qs = qs.filter(status=status)

    # Monta a lista final
    for a in qs.order_by('-data_inicio')[:200]:
        dentro_janela = (a.data_inicio is None or a.data_inicio <= hoje) and (a.data_fim is None or a.data_fim >= hoje)
        if a.status == 'LIBERADO' and dentro_janela:
            status_final = 'LIBERADO'
        elif a.status == 'BLOQUEADO':
            status_final = 'BLOQUEADO'
        else:
            status_final = 'PENDENTE'

        resultados.append({
            'status_final': status_final,
            'nome': a.colaborador.nome,
            'empresa': a.colaborador.empresa.nome if a.colaborador.empresa else '—',
            'funcao': a.colaborador.funcao or '—',
            'placa': a.veiculo.placa if a.veiculo else None,
            'local': a.local or '—',
            'data_inicio': a.data_inicio,
            'data_fim': a.data_fim,
        })

    contexto = {
        "termo": termo,
        "resultados": resultados,
        "somente_hoje": somente_hoje,
        "data_de": data_de,
        "data_ate": data_ate,
        "status": status,
    }
    return render(request, "core/portaria_busca.html", contexto)

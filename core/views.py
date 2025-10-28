# core/views.py
import re
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import (
    EmpresaForm,
    ColaboradorForm,
    VeiculoForm,
    AcessoForm,
    UploadArquivoForm,
)
from .models import Empresa, Colaborador, Veiculo, Atribuicao, Acesso


def _limpa_cpf(termo: str):
    digits = re.sub(r"\D+", "", termo or "")
    return digits if len(digits) == 11 else None


def _limpa_placa(termo: str):
    if not termo:
        return None
    placa = re.sub(r"[^A-Za-z0-9]", "", termo).upper()
    return placa if 7 <= len(placa) <= 8 else None


def portaria_busca(request):
    """
    Tela principal, busca por nome, empresa, CPF ou placa.
    """
    termo = request.GET.get("q", "").strip()
    resultados = []

    if termo:
        hoje = date.today()
        cpf = _limpa_cpf(termo)
        placa = _limpa_placa(termo)

        qs = (
            Atribuicao.objects
            .select_related("colaborador", "veiculo", "colaborador__empresa")
            .order_by("-data_inicio")
        )

        if placa:
            qs = qs.filter(veiculo__placa=placa)
        elif cpf:
            qs = qs.filter(colaborador__cpf=cpf)
        else:
            qs = qs.filter(
                Q(colaborador_nome_icontains=termo) |
                Q(colaborador_empresanome_icontains=termo)
            )

        for a in qs[:200]:
            dentro_janela = (
                (a.data_inicio is None or a.data_inicio <= hoje)
                and (a.data_fim is None or a.data_fim >= hoje)
            )
            if a.status == "LIBERADO" and dentro_janela:
                status_final = "LIBERADO"
            elif a.status == "BLOQUEADO":
                status_final = "BLOQUEADO"
            else:
                status_final = "PENDENTE"

            resultados.append({
                "status_final": status_final,
                "nome": a.colaborador.nome,
                "empresa": a.colaborador.empresa.nome if a.colaborador.empresa else "",
                "funcao": a.colaborador.funcao or "",
                "placa": a.veiculo.placa if a.veiculo else "",
                "local": a.local or "",
                "data_inicio": a.data_inicio,
                "data_fim": a.data_fim,
            })

    return render(request, "core/portaria_busca.html", {"termo": termo, "resultados": resultados})


# ---------- Cadastros ----------
@login_required
@permission_required("core.add_empresa", raise_exception=True)
def empresa_criar(request):
    form = EmpresaForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Empresa cadastrada com sucesso.")
        return redirect("empresa_criar")
    return render(request, "core/form.html", {"titulo": "Cadastrar Empresa", "form": form})


@login_required
@permission_required("core.add_colaborador", raise_exception=True)
def colaborador_criar(request):
    form = ColaboradorForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Colaborador cadastrado com sucesso.")
        return redirect("colaborador_criar")
    return render(request, "core/form.html", {"titulo": "Cadastrar Colaborador", "form": form})


@login_required
@permission_required("core.add_veiculo", raise_exception=True)
def veiculo_criar(request):
    form = VeiculoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Veículo cadastrado com sucesso.")
        return redirect("veiculo_criar")
    return render(request, "core/form.html", {"titulo": "Cadastrar Veículo", "form": form})


@login_required
@permission_required("core.add_atribuicao", raise_exception=True)
def acesso_criar(request):
    form = AcessoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Atribuição criada com sucesso.")
        return redirect("acesso_criar")
    return render(request, "core/form.html", {"titulo": "Cadastrar Atribuição", "form": form})


# ---------- Home dos cadastros ----------
@login_required
def cadastro_home(request):
    return render(request, "core/cadastro_home.html")


# ---------- Upload em lote ----------
@login_required
def upload_lotes(request):
    """
    Apenas exibe o formulário por enquanto.
    A lógica de processar arquivos vem depois.
    """
    if request.method == "POST":
        form = UploadArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, "Arquivo recebido com sucesso.")
            return redirect("upload_lotes")
    else:
        form = UploadArquivoForm()
    return render(request, "core/upload.html", {"form": form})
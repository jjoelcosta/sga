# core/views.py
import re
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render, redirect
from . import importers
from django.core.paginator import Paginator

@login_required
def empresa_listar(request):
    q = request.GET.get("q", "").strip()
    qs = Empresa.objects.all().order_by("nome")
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(cnpj__icontains=q) | Q(responsavel__icontains=q)
        )
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "core/lista_empresas.html", {"page_obj": page_obj, "q": q})

@login_required
def colaborador_listar(request):
    q = request.GET.get("q", "").strip()
    qs = Colaborador.objects.select_related("empresa").all().order_by("nome")
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) | Q(cpf__icontains=q) | Q(funcao__icontains=q) | Q(empresa__nome__icontains=q)
        )
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "core/lista_colaboradores.html", {"page_obj": page_obj, "q": q})

@login_required
def veiculo_listar(request):
    q = request.GET.get("q", "").strip()
    qs = Veiculo.objects.select_related("colaborador", "colaborador__empresa").all().order_by("placa")
    if q:
        qs = qs.filter(
            Q(placa__icontains=q) | Q(modelo__icontains=q) | Q(marca__icontains=q) |
            Q(colaborador__nome__icontains=q) | Q(colaborador__empresa__nome__icontains=q)
        )
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    return render(request, "core/lista_veiculos.html", {"page_obj": page_obj, "q": q})


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
                Q(colaborador_nomeicontains=termo) | Q(colaboradorempresanome_icontains=termo)
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
    Recebe CSV ou XLSX, chama o importador, cria registro no histórico
    e mostra mensagem com o resumo.
    """
    if request.method == "POST":
        form = UploadArquivoForm(request.POST, request.FILES)
        if form.is_valid():
            tipo = form.cleaned_data["tipo"]
            f = form.cleaned_data["arquivo"]

            # salva histórico parcial
            from .models import LoteImportacao
            hist = LoteImportacao.objects.create(
                tipo=tipo,
                arquivo_nome=f.name,
                ok=False,
                total_processado=0,
                total_erros=0,
                log="Recebido para processamento.",
            )

            # chama o importador
            try:
                from . import importers  # core/importers.py
                resumo = importers.importar_arquivo(file_obj=f, tipo=tipo)
                # esperado um dicionário como:
                # {"ok": True/False, "criados_ou_atualizados": N, "erros": ["msg1","msg2", ...]}
                ok = bool(resumo.get("ok"))
                total = int(resumo.get("criados_ou_atualizados", 0))
                erros = resumo.get("erros", [])
                hist.ok = ok
                hist.total_processado = total
                hist.total_erros = len(erros)
                if erros:
                    hist.log = "\n".join(erros[:50])
                else:
                    hist.log = "Processado sem erros."
                hist.save()

                if ok:
                    messages.success(
                        request,
                        f"Upload processado com sucesso, {total} registros afetados."
                    )
                else:
                    messages.warning(
                        request,
                        f"Upload processado com avisos, {total} registros afetados, {len(erros)} erros."
                    )
            except Exception as e:
                # registra falha
                hist.ok = False
                hist.total_processado = 0
                hist.total_erros = 1
                hist.log = f"Falha ao processar, {e}"
                hist.save()
                messages.error(request, f"Falha no processamento, {e}")

            return redirect("upload_lotes")
    else:
        form = UploadArquivoForm()

    # lista últimos uploads no rodapé
    from .models import LoteImportacao
    ultimos = LoteImportacao.objects.order_by("-criado_em")[:10]
    return render(request, "core/upload.html", {"form": form, "uploads": ultimos})
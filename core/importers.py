# core/importers.py
from __future__ import annotations

import csv
from datetime import datetime
from typing import IO, Tuple, List

from django.db import transaction
from openpyxl import load_workbook

from .models import Empresa, Colaborador, Veiculo, Atribuicao

# Helpers simples
def _norm(s: str) -> str:
    return (s or "").strip()

def _read_xlsx(fp: IO):
    wb = load_workbook(fp, data_only=True)
    ws = wb.active
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            headers = [(_norm(h) or f"col_{idx}") for idx, h in enumerate(row)]
            continue
        rows.append({headers[j]: (row[j] if row and j < len(row) else None) for j in range(len(headers))})
    return rows

def _read_csv(fp: IO):
    # tenta utf-8, se falhar tenta latin1
    data = fp.read()
    if isinstance(data, bytes):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin1")
    else:
        text = data
    reader = csv.DictReader(text.splitlines())
    return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in reader]

def _open_rows(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx"):
        return _read_xlsx(uploaded_file.file)
    if name.endswith(".csv"):
        return _read_csv(uploaded_file.file)
    raise ValueError("Formato não suportado, use CSV ou XLSX.")

# Importadores
@transaction.atomic
def importar_empresas(uploaded_file) -> Tuple[int, List[str]]:
    rows = _open_rows(uploaded_file)
    ok, erros = 0, []
    for i, r in enumerate(rows, start=2):
        cnpj = _norm(str(r.get("CNPJ") or r.get("cnpj") or ""))
        nome = _norm(str(r.get("Nome") or r.get("nome") or ""))
        responsavel = _norm(str(r.get("Responsavel") or r.get("responsavel") or ""))
        telefone = _norm(str(r.get("Telefone") or r.get("telefone") or ""))

        if not cnpj or not nome:
            erros.append(f"Linha {i}: faltando CNPJ ou Nome")
            continue

        Empresa.objects.update_or_create(
            cnpj=cnpj,
            defaults={"nome": nome, "responsavel": responsavel, "telefone": telefone},
        )
        ok += 1
    return ok, erros

@transaction.atomic
def importar_colaboradores(uploaded_file) -> Tuple[int, List[str]]:
    rows = _open_rows(uploaded_file)
    ok, erros = 0, []
    for i, r in enumerate(rows, start=2):
        cpf = _norm(str(r.get("CPF") or r.get("cpf") or ""))
        nome = _norm(str(r.get("Nome") or r.get("nome") or ""))
        funcao = _norm(str(r.get("Funcao") or r.get("função") or r.get("funcao") or ""))
        emp_cnpj = _norm(str(r.get("Empresa_CNPJ") or r.get("empresa_cnpj") or ""))

        if not cpf or not nome or not emp_cnpj:
            erros.append(f"Linha {i}: faltando CPF, Nome ou Empresa_CNPJ")
            continue

        try:
            empresa = Empresa.objects.get(cnpj=emp_cnpj)
        except Empresa.DoesNotExist:
            erros.append(f"Linha {i}: Empresa {emp_cnpj} não encontrada")
            continue

        Colaborador.objects.update_or_create(
            cpf=cpf,
            defaults={"nome": nome, "funcao": funcao, "empresa": empresa},
        )
        ok += 1
    return ok, erros

@transaction.atomic
def importar_veiculos(uploaded_file) -> Tuple[int, List[str]]:
    rows = _open_rows(uploaded_file)
    ok, erros = 0, []
    for i, r in enumerate(rows, start=2):
        placa = _norm(str(r.get("Placa") or r.get("placa") or "")).upper()
        marca = _norm(str(r.get("Marca") or r.get("marca") or ""))
        modelo = _norm(str(r.get("Modelo") or r.get("modelo") or ""))
        cor = _norm(str(r.get("Cor") or r.get("cor") or ""))
        cpf = _norm(str(r.get("CPF") or r.get("cpf") or ""))

        if not placa:
            erros.append(f"Linha {i}: faltando Placa")
            continue

        colab = None
        if cpf:
            colab = Colaborador.objects.filter(cpf=cpf).first()
            if not colab:
                erros.append(f"Linha {i}: Colaborador CPF {cpf} não encontrado, veículo será criado sem vínculo")

        Veiculo.objects.update_or_create(
            placa=placa,
            defaults={"marca": marca, "modelo": modelo, "cor": cor, "colaborador": colab},
        )
        ok += 1
    return ok, erros

@transaction.atomic
def importar_atribuicoes(uploaded_file) -> Tuple[int, List[str]]:
    rows = _open_rows(uploaded_file)
    ok, erros = 0, []
    for i, r in enumerate(rows, start=2):
        cpf = _norm(str(r.get("CPF") or r.get("cpf") or ""))
        placa = _norm(str(r.get("Placa") or r.get("placa") or "")).upper()
        local = _norm(str(r.get("Local") or r.get("local") or ""))
        di = _norm(str(r.get("DataInicio") or r.get("data_inicio") or ""))
        df = _norm(str(r.get("DataFim") or r.get("data_fim") or ""))
        status = _norm(str(r.get("Status") or r.get("status") or "PENDENTE")).upper() or "PENDENTE"

        if not cpf or not local or not di:
            erros.append(f"Linha {i}: faltando CPF, Local ou DataInicio")
            continue

        colab = Colaborador.objects.filter(cpf=cpf).first()
        if not colab:
            erros.append(f"Linha {i}: Colaborador CPF {cpf} não encontrado")
            continue

        veic = None
        if placa:
            veic = Veiculo.objects.filter(placa=placa).first()
            if not veic:
                erros.append(f"Linha {i}: Veículo placa {placa} não encontrado, atribuição seguirá sem veículo")

        # tenta vários formatos de data
        def parse_date(s):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(s, fmt).date()
                except Exception:
                    pass
            return None

        d_inicio = parse_date(di)
        d_fim = parse_date(df) if df else None
        if not d_inicio:
            erros.append(f"Linha {i}: DataInicio inválida")
            continue

        Atribuicao.objects.create(
            colaborador=colab,
            veiculo=veic,
            local=local,
            data_inicio=d_inicio,
            data_fim=d_fim,
            status=status if status in {"LIBERADO", "PENDENTE", "BLOQUEADO"} else "PENDENTE",
        )
        ok += 1
    return ok, erros

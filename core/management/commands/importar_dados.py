import pandas as pd
import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pathlib import Path
from core.models import Empresa, Colaborador, Veiculo, Atribuicao
from datetime import datetime


class Command(BaseCommand):
    help = 'Importa dados de empresas, colaboradores, veículos e atribuições de um arquivo CSV ou XLSX.'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', type=str, help='Caminho para o arquivo CSV/XLSX')
        parser.add_argument('--tipo', type=str, required=True,
                            choices=['empresa', 'colaborador', 'veiculo', 'atribuicao'],
                            help='Tipo de dado a ser importado.')

    def handle(self, *args, **options):
        arquivo_path = options['arquivo']
        tipo_dado = options['tipo']
        caminho = Path(arquivo_path)

        if not caminho.exists():
            raise CommandError(f'Arquivo não encontrado: {arquivo_path}')

        if caminho.suffix.lower() == '.csv':
            df = pd.read_csv(caminho, dtype=str)
        elif caminho.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(caminho, dtype=str)
        else:
            raise CommandError('Formato de arquivo não suportado. Use CSV ou XLSX.')

        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

        registros_criados = 0
        erros = []

        with transaction.atomic():
            if tipo_dado == 'empresa':
                registros_criados, erros = self._importar_empresas(df)
            elif tipo_dado == 'colaborador':
                registros_criados, erros = self._importar_colaboradores(df)
            elif tipo_dado == 'veiculo':
                registros_criados, erros = self._importar_veiculos(df)
            elif tipo_dado == 'atribuicao':
                registros_criados, erros = self._importar_atribuicoes(df)

        self.stdout.write(self.style.SUCCESS(f'\nImportação de {tipo_dado} concluída!'))
        self.stdout.write(f'{registros_criados} registros criados ou atualizados.')

        if erros:
            self.stdout.write(self.style.WARNING(f'{len(erros)} erros encontrados. (Mostrando os primeiros 5)'))
            for erro in erros[:5]:
                self.stdout.write(self.style.ERROR(erro))

    def _importar_empresas(self, df):
        erros, criados = [], 0
        for i, row in df.iterrows():
            try:
                cnpj = re.sub(r'\D', '', row.get('cnpj', ''))
                Empresa.objects.update_or_create(
                    cnpj=cnpj,
                    defaults={'nome': row.get('nome', ''),
                              'responsavel': row.get('responsavel', ''),
                              'telefone': row.get('telefone', '')}
                )
                criados += 1
            except Exception as e:
                erros.append(f"Linha {i+2}: {e}")
        return criados, erros

    def _importar_colaboradores(self, df):
        erros, criados = [], 0
        for i, row in df.iterrows():
            try:
                empresa = Empresa.objects.filter(cnpj=re.sub(r'\D', '', row.get('cnpj_empresa', ''))).first()
                if not empresa:
                    raise ValueError("Empresa não encontrada")
                Colaborador.objects.update_or_create(
                    cpf=re.sub(r'\D', '', row.get('cpf', '')),
                    defaults={'empresa': empresa,
                              'nome': row.get('nome', ''),
                              'funcao': row.get('funcao', '')}
                )
                criados += 1
            except Exception as e:
                erros.append(f"Linha {i+2}: {e}")
        return criados, erros

    def _importar_veiculos(self, df):
        erros, criados = [], 0
        for i, row in df.iterrows():
            try:
                colaborador = Colaborador.objects.filter(cpf=re.sub(r'\D', '', row.get('cpf_colaborador', ''))).first()
                Veiculo.objects.update_or_create(
                    placa=row.get('placa', '').upper(),
                    defaults={'colaborador': colaborador,
                              'modelo': row.get('modelo', ''),
                              'marca': row.get('marca', ''),
                              'cor': row.get('cor', '')}
                )
                criados += 1
            except Exception as e:
                erros.append(f"Linha {i+2}: {e}")
        return criados, erros

    def _importar_atribuicoes(self, df):
        erros, criados = [], 0
        for i, row in df.iterrows():
            try:
                colaborador = Colaborador.objects.filter(cpf=re.sub(r'\D', '', row.get('cpf', ''))).first()
                veiculo = Veiculo.objects.filter(placa=row.get('placa', '').upper()).first()
                Atribuicao.objects.create(
                    colaborador=colaborador,
                    veiculo=veiculo,
                    local=row.get('local', 'Portaria A'),
                    data_inicio=pd.to_datetime(row.get('data_inicio')).date(),
                    data_fim=pd.to_datetime(row.get('data_fim')).date(),
                    status=row.get('status', 'PENDENTE'),
                )
                criados += 1
            except Exception as e:
                erros.append(f"Linha {i+2}: {e}")
        return criados, erros

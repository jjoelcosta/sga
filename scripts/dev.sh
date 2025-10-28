#!/usr/bin/env bash

set -e

DJ="python manage.py"

case "$1" in
  check)
    $DJ check
    ;;
  run)
    $DJ runserver
    ;;
  mig)
    $DJ makemigrations
    $DJ migrate
    ;;
  super)
    $DJ createsuperuser
    ;;
  shell)
    $DJ shell
    ;;
  import_emp)
    $DJ importar_dados importacoes/dados_empresas.xlsx --tipo empresa
    ;;
  import_col)
    $DJ importar_dados importacoes/dados_colaboradores.xlsx --tipo colaborador
    ;;
  import_vei)
    $DJ importar_dados importacoes/dados_veiculos.xlsx --tipo veiculo
    ;;
  import_att)
    $DJ importar_dados importacoes/dados_atribuicoes.xlsx --tipo atribuicao
    ;;
  *)
    echo "Uso: scripts/dev.sh {check|run|mig|super|shell|import_emp|import_col|import_vei|import_att}"
    exit 1
    ;;
esac

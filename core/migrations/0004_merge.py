from django.db import migrations

class Migration(migrations.Migration):

    # declare ambas as migrations conflitantes como dependências
    dependencies = [
        ("core", "0001_auto_add_timestamps_and_audit"),
        ("core", "0003_loteimportacao_acesso"),
    ]

    # nenhuma operação necessária: este migration apenas resolve o grafo (merge)
    operations = []
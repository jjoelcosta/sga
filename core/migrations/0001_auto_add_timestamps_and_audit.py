from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add timestamp fields to models
        migrations.AddField(
            model_name='empresa',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='empresa',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='colaborador',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='colaborador',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='veiculo',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='veiculo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='atribuicao',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='atribuicao',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='acesso',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='acesso',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='loteimportacao',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='loteimportacao',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        # Add auditoria fields to Acesso
        migrations.AddField(
            model_name='acesso',
            name='criado_por',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acessos_criados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='acesso',
            name='dispositivo',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='acesso',
            name='ip_address',
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
        # Change LoteImportacao.log field to JSONField (may be noop on DBs that already store JSON)
        migrations.AlterField(
            model_name='loteimportacao',
            name='log',
            field=models.JSONField(blank=True, null=True),
        ),
    ]

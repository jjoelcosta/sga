from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import LoteImportacao
import json

class Command(BaseCommand):
    help = "Converte LoteImportacao.log de texto para JSON quando necessário (não destrutivo)."

    def handle(self, *args, **options):
        total = 0
        updated = 0
        errors = 0
        qs = LoteImportacao.objects.all()
        for obj in qs:
            total += 1
            val = obj.log
            # Se já for dict/list (ou None), pular
            if isinstance(val, (dict, list)) or val is None:
                continue
            try:
                # tenta parsear se for string JSON
                parsed = json.loads(val)
                obj.log = parsed
                with transaction.atomic():
                    obj.save(update_fields=["log"])
                updated += 1
            except Exception:
                # não é JSON: encapsula como mensagem
                try:
                    obj.log = {"mensagem": str(val)}
                    with transaction.atomic():
                        obj.save(update_fields=["log"])
                    updated += 1
                except Exception as e:
                    errors += 1
                    self.stderr.write(f"Erro ao atualizar id={{obj.pk}}: {{e}}")
        self.stdout.write(f"Total: {{total}} — Atualizados: {{updated}} — Erros: {{errors}}")

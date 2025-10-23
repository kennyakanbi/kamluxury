# listings/management/commands/load_render_fixture.py
from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
from pathlib import Path
import sys

class Command(BaseCommand):
    help = "Load render_data.json fixture if it exists in project root."

    def handle(self, *args, **options):
        fixture = Path.cwd() / "render_data.json"
        if not fixture.exists():
            self.stdout.write("No render_data.json found — skipping fixture load.")
            return

        try:
            with fixture.open("r", encoding="utf-8") as fh:
                objs = list(serializers.deserialize("json", fh))
            if not objs:
                self.stdout.write("Fixture is empty.")
                return

            with transaction.atomic():
                count = 0
                for obj in objs:
                    obj.save()
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"Loaded {count} objects from render_data.json"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to load fixture: {exc}"))
            raise

# listings/management/commands/audit_media.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from listings.models import Property

FIELDS = ['cover', 'gallery1', 'gallery2']

class Command(BaseCommand):
    help = "Audit Property media fields: local existence, http URLs, empty."

    def handle(self, *args, **kwargs):
        qs = Property.objects.all()
        total = qs.count()
        print(f"Found {total} properties. Scanning...")
        missing_local = []
        http_fields = []
        present_local = []
        empty = []

        for p in qs:
            for f in FIELDS:
                if not hasattr(p, f):
                    continue
                val = getattr(p, f)
                if not val:
                    empty.append((p.id, p.title, f, None))
                    continue
                s = str(val)
                if s.startswith('http://') or s.startswith('https://'):
                    http_fields.append((p.id, p.title, f, s))
                else:
                    local_path = None
                    if hasattr(val, 'path'):
                        try:
                            local_path = val.path
                        except Exception:
                            local_path = None
                    if not local_path:
                        candidate = os.path.join(settings.MEDIA_ROOT, s.lstrip('/'))
                        local_path = candidate
                    if os.path.exists(local_path):
                        present_local.append((p.id, p.title, f, local_path))
                    else:
                        missing_local.append((p.id, p.title, f, local_path or s))

        print("=== SUMMARY ===")
        print("Empty fields:", len(empty))
        print("Fields already HTTP/URL:", len(http_fields))
        print("Present locally:", len(present_local))
        print("Missing locally:", len(missing_local))
        if missing_local:
            print("\nMissing examples (id, title, field, path):")
            for m in missing_local[:20]:
                print(m)
        if http_fields:
            print("\nHTTP field examples (id, title, field, url):")
            for m in http_fields[:20]:
                print(m)
        print("Done.")

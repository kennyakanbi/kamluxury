# listings/management/commands/migrate_to_cloudinary_v2.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from cloudinary.uploader import upload as cloudinary_upload
from django.db import transaction
from listings.models import Property

FIELDS = ['cover', 'gallery1', 'gallery2']

class Command(BaseCommand):
    help = "Upload local media files to Cloudinary; store public_id for CloudinaryField, secure_url for others."

    def handle(self, *args, **kwargs):
        props = Property.objects.all()
        total = props.count()
        print(f"Found {total} properties. Starting migration...")

        for idx, p in enumerate(props, start=1):
            updated = False
            for f in FIELDS:
                if not hasattr(p, f):
                    continue
                val = getattr(p, f)
                if not val:
                    continue
                s = str(val)
                if s.startswith('http://') or s.startswith('https://'):
                    print(f"[{idx}/{total}] {p.title} {f} already URL, skipping.")
                    continue

                local_path = None
                if hasattr(val, 'path'):
                    try:
                        local_path = val.path
                    except Exception:
                        local_path = None
                if not local_path:
                    local_path = os.path.join(settings.MEDIA_ROOT, s.lstrip('/'))

                if not os.path.exists(local_path):
                    print(f"[{idx}/{total}] File missing: {local_path} (DB: {s}) — skipping.")
                    continue

                try:
                    res = cloudinary_upload(local_path, folder="properties")
                    public_id = res.get('public_id')
                    secure_url = res.get('secure_url') or res.get('url')
                except Exception as exc:
                    print(f"[{idx}/{total}] Upload failed for {p.title} {f}: {exc}")
                    continue

                try:
                    model_field = p._meta.get_field(f)
                    field_class_name = model_field.__class__.__name__
                except Exception:
                    field_class_name = ''

                if 'Cloudinary' in field_class_name:
                    setattr(p, f, public_id)
                    print(f"[{idx}/{total}] Uploaded and saved public_id for {p.title} {f}: {public_id}")
                else:
                    setattr(p, f, secure_url)
                    print(f"[{idx}/{total}] Uploaded and saved secure_url for {p.title} {f}: {secure_url}")

                updated = True

            if updated:
                try:
                    with transaction.atomic():
                        p.save()
                        print(f"[{idx}/{total}] Saved DB for {p.title}")
                except Exception as exc:
                    print(f"[{idx}/{total}] Failed to save DB for {p.title}: {exc}")

        print("Migration completed.")

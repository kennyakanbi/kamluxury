# listings/management/commands/migrate_media_to_cloudinary_secureurl.py
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from listings.models import Property
import cloudinary.uploader

class Command(BaseCommand):
    help = "Upload local media files (media/properties/*) to Cloudinary and set Property.cover/gallery fields to the secure_url."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Do not modify DB; only show what would be done.")
        parser.add_argument("--limit", type=int, default=0, help="Process only N properties (0 = all).")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        limit = options["limit"]
        base_media = getattr(settings, "MEDIA_ROOT", None) or (Path(settings.BASE_DIR) / "media")
        self.stdout.write(f"media root: {base_media}")
        qs = Property.objects.all()
        if limit:
            qs = qs[:limit]

        fields = ("cover", "gallery1", "gallery2")
        for p in qs:
            for field_name in fields:
                field = getattr(p, field_name, None)
                if not field:
                    continue
                name = getattr(field, "name", None) or str(field)
                url = getattr(field, "url", None)
                # skip if already cloudinary url
                if url and "res.cloudinary.com" in url:
                    self.stdout.write(f"[SKIP] {p.pk} {field_name} already cloudinary: {url}")
                    continue

                # try local path
                local_path = getattr(field, "path", None)
                if not local_path and name:
                    local_path = os.path.join(base_media, name)

                if not local_path or not os.path.exists(local_path):
                    self.stdout.write(f"[MISSING] {p.pk} {field_name} file not found at {local_path} (name={name})")
                    continue

                self.stdout.write(f"[UPLOAD] {p.pk} {field_name} -> uploading {local_path}")
                if dry:
                    continue

                try:
                    res = cloudinary.uploader.upload(local_path, folder="properties")
                except Exception as e:
                    self.stderr.write(f"[ERROR] upload failed for {local_path}: {e}")
                    continue

                secure_url = res.get("secure_url")
                public_id  = res.get("public_id")
                if not secure_url:
                    self.stderr.write(f"[ERROR] no secure_url returned for {local_path}")
                    continue

                # Save secure_url to the model field (string). This is straightforward and works
                # even if your DEFAULT_FILE_STORAGE differs locally vs deployed.
                setattr(p, field_name, secure_url)
                try:
                    p.save(update_fields=[field_name])
                    self.stdout.write(f"[UPDATED] {p.pk} {field_name} -> {secure_url}")
                except Exception as e:
                    self.stderr.write(f"[ERROR] saving model failed: {e}")
        self.stdout.write("Done.")

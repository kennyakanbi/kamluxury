# listings/management/commands/upload_missing_to_cloudinary.py
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from cloudinary import uploader, api
from listings.models import Property

MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", Path(__file__).resolve().parents[3] / "media"))

def is_cloudinary_public_id(value: str):
    if not value:
        return False
    s = str(value)
    # a simple heuristic: contains folder 'properties/' and no leading http
    return "properties/" in s and not s.startswith("http")

def public_id_from_db_value(value: str):
    # Accept values like: "properties/name.jpg" or "properties/name"
    if not value:
        return None
    s = str(value)
    if s.startswith("http"):
        # extract after /upload/ and drop version if present
        try:
            part = s.split("/upload/")[1]
            if part.startswith("v") and "/" in part:
                part = "/".join(part.split("/")[1:])
            public_id = part.rsplit(".", 1)[0]
            return public_id
        except Exception:
            return None
    else:
        return s.rsplit(".", 1)[0] if "." in s else s

class Command(BaseCommand):
    help = "Upload missing local media files referenced by Property model to Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Don't save DB changes; just report.")
        parser.add_argument("--folder", default="properties", help="Cloudinary folder to upload to (default: properties)")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        folder = options["folder"]
        props = Property.objects.all()
        total = props.count()
        self.stdout.write(f"Found {total} properties. Scanning...")

        updated = 0
        for idx, p in enumerate(props, start=1):
            self.stdout.write(f"[{idx}/{total}] Property {p.id} - {p.title}")
            changed = False

            for field_name in ("cover", "gallery1", "gallery2"):
                field = getattr(p, field_name)
                raw = str(field) if field else ""
                public_candidate = public_id_from_db_value(raw)

                # 1) If DB already points to a cloudinary public id, check Cloudinary for resource existence
                if public_candidate and is_cloudinary_public_id(raw):
                    try:
                        api.resource(public_candidate)
                        self.stdout.write(f"  {field_name}: already on Cloudinary ({public_candidate}) -> skip")
                        continue
                    except Exception as e:
                        # Not found or auth error -> we may try to upload local file if present
                        self.stdout.write(f"  {field_name}: Cloudinary check: {e} (will try local upload if file present)")

                # 2) Try local file path: prefer field.path if available; otherwise, construct from MEDIA_ROOT + raw name
                local_path = None
                try:
                    # if FileField with path attribute
                    if hasattr(field, "path"):
                        local_path = Path(field.path)
                    else:
                        if raw:
                            local_path = MEDIA_ROOT / raw
                except Exception:
                    local_path = None

                if local_path and local_path.exists():
                    # upload to cloudinary
                    try:
                        self.stdout.write(f"  {field_name}: uploading local file {local_path} -> Cloudinary/{folder}")
                        res = uploader.upload(str(local_path), folder=folder)
                        # res['public_id'] will be like 'properties/name' (without extension)
                        ext = local_path.suffix.lstrip(".").lower()
                        public_with_ext = f"{res['public_id']}.{ext}" if ext else res['public_id']
                        if not dry:
                            setattr(p, field_name, public_with_ext)
                            changed = True
                        self.stdout.write(f"    uploaded -> {public_with_ext}")
                    except Exception as e:
                        self.stdout.write(f"    ERROR uploading {local_path}: {e}")
                else:
                    self.stdout.write(f"  {field_name}: no local file found for DB value '{raw}' -> skipping")

            if changed and not dry:
                p.save()
                updated += 1
                self.stdout.write(f"  [SAVED] Property {p.id}")

        self.stdout.write(f"Done. Updated {updated}")

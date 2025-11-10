# listings/management/commands/normalize_cloudinary_fields.py
import re
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from listings.models import Property

def public_id_from_url(url):
    """
    Extract the Cloudinary public_id+ext from a secure_url or url.
    Examples:
      https://res.cloudinary.com/xxx/image/upload/v123/properties/name.jpg
      -> properties/name.jpg

      https://res.cloudinary.com/xxx/image/upload/properties/name.jpg
      -> properties/name.jpg

      or full http-escaped urls -> handle robustly.
    """
    if not url:
        return None
    try:
        # split after '/upload/'
        if "/upload/" in url:
            part = url.split("/upload/", 1)[1]
        else:
            # fallback: remove domain
            parsed = urlparse(url)
            part = parsed.path.lstrip('/')
        # remove version prefix like v12345/
        part = re.sub(r"^v\d+/", "", part)
        # unquote percent-encoding if any
        from urllib.parse import unquote
        part = unquote(part)
        return part  # e.g. properties/name.jpg
    except Exception:
        return None

class Command(BaseCommand):
    help = "Normalize Cloudinary-backed fields: replace full https://... URLs saved in DB with Cloudinary public_id/path."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually write changes to DB. Without --apply the command runs in dry-run mode and prints what would change.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        fields = ["cover", "gallery1", "gallery2"]
        props = Property.objects.all()
        total = props.count()
        self.stdout.write(f"Found {total} properties. Scanning... (apply={apply_changes})")

        changes = []
        for p in props:
            for f in fields:
                val = getattr(p, f)
                sval = str(val) if val else ""
                if sval.startswith("http"):
                    public = public_id_from_url(sval)
                    if not public:
                        self.stdout.write(f"[WARN] Could not extract public_id for Property {p.id} {p.title} ({f}): {sval}")
                        continue
                    # if value already equal to extracted part, skip
                    if sval.endswith(public):
                        # candidate public extracted
                        self.stdout.write(f"[OK ] Property {p.id} {p.title} ({f}) -> would replace URL with '{public}'")
                        if apply_changes:
                            setattr(p, f, public)
                            # mark changed, but save once per object later
                            changes.append(p)
                    else:
                        self.stdout.write(f"[NOTE] Property {p.id} {p.title} ({f}) extracted '{public}' from '{sval}'")
                        if apply_changes:
                            setattr(p, f, public)
                            changes.append(p)

        if apply_changes:
            # remove duplicates and save
            saved_ids = set()
            for p in changes:
                if p.id in saved_ids:
                    continue
                p.save()
                saved_ids.add(p.id)
                self.stdout.write(f"[SAVED] Property {p.id} {p.title} saved.")
            self.stdout.write(f"Done. Updated {len(saved_ids)} properties.")
        else:
            self.stdout.write("Dry-run complete. No DB changes made. Re-run with --apply to write changes.")

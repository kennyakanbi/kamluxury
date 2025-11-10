from django.core.management.base import BaseCommand
from django.conf import settings
from listings.models import Property
import os
import cloudinary.uploader

PLACEHOLDER_LOCAL = os.path.join(settings.BASE_DIR, "static", "img", "placeholder_600x400.png")
# folder/path you want Cloudinary to use
CLOUD_FOLDER = "properties"

class Command(BaseCommand):
    help = "Upload local placeholder image to Cloudinary and replace placeholder fields."

    def handle(self, *args, **options):
        if not os.path.exists(PLACEHOLDER_LOCAL):
            self.stdout.write(self.style.ERROR(f"Placeholder file not found: {PLACEHOLDER_LOCAL}"))
            return

        # make sure CLOUDINARY_URL or cloudinary config is set
        try:
            # upload only once to Cloudinary and reuse the resulting url/public_id
            res = cloudinary.uploader.upload(PLACEHOLDER_LOCAL, folder=CLOUD_FOLDER, use_filename=True, unique_filename=False)
            cloud_url = res.get("secure_url") or res.get("url")
            public_id = res.get("public_id")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cloudinary upload failed: {e}"))
            return

        if not cloud_url:
            self.stdout.write(self.style.ERROR("Cloudinary upload returned no URL."))
            return

        replaced = 0
        for p in Property.objects.all():
            changed = False
            for field_name in ("cover", "gallery1", "gallery2"):
                f = getattr(p, field_name, None)
                url = getattr(f, "url", "") or ""
                # detect placeholder / local references — adjust condition to suit your DB
                if url.endswith("placeholder_600x400.png") or url.startswith("/media/") or "res.cloudinary.com" not in url:
                    # If using CloudinaryField, assign the Cloudinary public_id so storage returns cloud URL.
                    try:
                        # if field is CloudinaryField, assign a Cloudinary resource object by saving file-like? Simple approach:
                        setattr(p, field_name, cloud_url)
                    except Exception:
                        # fallback: set field to URL string (for CharField-like cases)
                        setattr(p, field_name, cloud_url)
                    changed = True

            if changed:
                p.save()
                replaced += 1
                self.stdout.write(self.style.SUCCESS(f"Updated {p.pk} {p.title} with placeholder image(s)."))

        self.stdout.write(self.style.SUCCESS(f"Done. Uploaded placeholder to Cloudinary: {cloud_url} (replaced in {replaced} properties)"))

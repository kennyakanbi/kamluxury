# listings/management/commands/upload_placeholders_to_cloudinary.py
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from listings.models import Property
import os

# optional dependency
try:
    import cloudinary.uploader
except Exception:
    cloudinary = None

# local placeholder path relative to project root (settings.BASE_DIR)
LOCAL_PLACEHOLDER = os.path.join(settings.BASE_DIR, "static", "img", "placeholder_600x400.png")
# fallback remote URL only used if local file missing
FALLBACK_PLACEHOLDER_URL = "https://via.placeholder.com/600x400"
CLOUD_FOLDER = "properties"

class Command(BaseCommand):
    help = "Upload placeholder image to Cloudinary (prefer local file) and replace placeholder/local URLs in Property image fields."

    def handle(self, *args, **options):
        # 1) ensure cloudinary is configured and available
        if cloudinary is None:
            self.stdout.write(self.style.ERROR("cloudinary package not found. Install `cloudinary` in your venv."))
            return

        # Check for CLOUDINARY_URL or explicit config
        cloud_conf = getattr(settings, "CLOUDINARY_URL", None)
        if not cloud_conf and not (settings.__dict__.get("CLOUDINARY", None)):
            # still allow cloudinary to be configured via env or settings module,
            # but warn if not found
            self.stdout.write(self.style.WARNING(
                "No obvious Cloudinary config found in settings. Make sure CLOUDINARY_URL or cloudinary.config() is set."
            ))

        # 2) determine placeholder source: local file preferred
        use_local = os.path.exists(LOCAL_PLACEHOLDER)
        if use_local:
            src_path = LOCAL_PLACEHOLDER
            self.stdout.write(f"Using local placeholder: {src_path}")
        else:
            src_path = FALLBACK_PLACEHOLDER_URL
            self.stdout.write(f"Local placeholder missing; will attempt to download: {src_path}")

        # 3) upload to Cloudinary
        try:
            if use_local:
                res = cloudinary.uploader.upload(src_path, folder=CLOUD_FOLDER, use_filename=True, unique_filename=False)
            else:
                # upload remote URL
                res = cloudinary.uploader.upload(src_path, folder=CLOUD_FOLDER)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Cloudinary upload failed: {exc}"))
            return

        cloud_url = res.get("secure_url") or res.get("url")
        public_id = res.get("public_id")
        if not cloud_url:
            self.stdout.write(self.style.ERROR("Upload succeeded but Cloudinary returned no URL."))
            return

        self.stdout.write(self.style.SUCCESS(f"Uploaded placeholder to Cloudinary: {cloud_url} (public_id: {public_id})"))

        # 4) replace placeholder/local images in DB
        updated = 0
        fields = ("cover", "gallery1", "gallery2")
        with transaction.atomic():
            for p in Property.objects.select_for_update().all():
                changed = False
                for fname in fields:
                    f = getattr(p, fname, None)
                    url = getattr(f, "url", "") or ""
                    # Flags identifying values to replace:
                    # - exact local placeholder saved as URL
                    # - stored value is local /media/ path
                    # - not a cloudinary url (heuristic)
                    if (
                        url.endswith("placeholder_600x400.png")
                        or url.startswith("/media/")
                        or "res.cloudinary.com" not in url
                    ):
                        # If field is a CloudinaryField, setting a url string may not be ideal,
                        # but in many setups CloudinaryField accepts a URL string and storage layer
                        # will produce the correct URL. We set the field to the secure cloud URL.
                        try:
                            setattr(p, fname, cloud_url)
                        except Exception:
                            # fallback: try setting attribute on filefield file
                            try:
                                getattr(p, fname).name = public_id
                            except Exception:
                                setattr(p, fname, cloud_url)
                        changed = True

                if changed:
                    p.save()
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated {p.pk} — {p.title}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Replaced images on {updated} properties."))

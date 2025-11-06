# listings/management/commands/migrate_property_covers.py
from pathlib import Path
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from listings.models import Property
import cloudinary.uploader

class Command(BaseCommand):
    help = "Upload local Property.cover files to Cloudinary and save secure URLs. Use --dry-run first."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Show what would be done without uploading.")
        parser.add_argument("--limit", type=int, default=0, help="Process at most N properties (0 = all).")
        parser.add_argument("--folder", type=str, default="properties", help="Cloudinary folder to upload to.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"] or 0
        folder = options["folder"]

        # MEDIA_ROOT fallback
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root:
            # fallback to BASE_DIR / "media" if MEDIA_ROOT not set
            base = getattr(settings, "BASE_DIR", Path(__file__).resolve().parents[3])
            media_root = Path(base) / "media"
        media_root = Path(media_root)

        qs = Property.objects.all().order_by("pk")
        if limit > 0:
            qs = qs[:limit]

        count = 0
        uploaded = 0
        skipped = 0
        missing_files = 0

        for p in qs:
            count += 1
            cover = getattr(p, "cover", None)
            cover_url = getattr(cover, "url", None) or ""
            cover_name = getattr(cover, "name", None)

            # If already a Cloudinary URL, skip
            if cover_url and "res.cloudinary.com" in cover_url:
                self.stdout.write(f"[SKIP] {p.pk} already on Cloudinary: {cover_url}")
                skipped += 1
                continue

            if not cover_name:
                self.stdout.write(f"[SKIP] {p.pk} no local name for cover (maybe blank): name={cover_name!r} url={cover_url!r}")
                skipped += 1
                continue

            local_path = media_root / cover_name
            if not local_path.exists():
                # sometimes files are stored under subdirectories, try join if cover_name is a path
                if os.path.isabs(cover_name) and Path(cover_name).exists():
                    local_path = Path(cover_name)
                else:
                    # last-ditch: check MEDIA_ROOT/<cover_name>
                    local_path = media_root / cover_name

            if not local_path.exists():
                self.stdout.write(f"[MISSING] {p.pk} expected file not found at {local_path}")
                missing_files += 1
                continue

            self.stdout.write(f"[OK] {p.pk} will upload: {local_path} -> /{folder}/ (dry_run={dry_run})")

            if dry_run:
                continue

            # Do the upload
            try:
                res = cloudinary.uploader.upload(
                    str(local_path),
                    folder=folder,
                    use_filename=True,
                    unique_filename=True,
                    overwrite=False,
                )
            except Exception as exc:
                self.stderr.write(f"[ERROR] Upload failed for {p.pk} {local_path}: {exc}")
                continue

            # Use secure_url returned by Cloudinary
            secure_url = res.get("secure_url") or res.get("url")
            public_id = res.get("public_id")

            if not secure_url:
                self.stderr.write(f"[ERROR] No secure_url returned for {p.pk}: {res!r}")
                continue

            # Save the URL as the field value — this works with CloudinaryField & CloudinaryStorage.
            # If your Cloudinary field expects a public_id instead, adjust accordingly.
            try:
                # assign string URL; depending on your field type you may prefer p.cover.name = public_id
                p.cover = secure_url
                p.save(update_fields=["cover"])
                uploaded += 1
                self.stdout.write(f"[UPLOADED] {p.pk} -> {secure_url} (public_id={public_id})")
            except Exception as exc:
                self.stderr.write(f"[ERROR] saving model for {p.pk}: {exc}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Scanned: {count}. Uploaded: {uploaded}. Skipped: {skipped}. Missing files: {missing_files}."
        ))

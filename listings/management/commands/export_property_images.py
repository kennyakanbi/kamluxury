# listings/management/commands/export_property_images.py
import csv
from django.core.management.base import BaseCommand
from listings.models import Property

PLACEHOLDER_FILENAME = "placeholder_600x400.png"  # adjust if you used a different name

def get_url(filefield):
    """Return string URL for a FileField-like object, or empty string."""
    return getattr(filefield, "url", "") or ""

def looks_missing_or_local(url):
    """Return True when url looks local or non-Cloudinary or is placeholder."""
    if not url:
        return True
    url = url.lower()
    if url.startswith("/media/"):
        return True
    if PLACEHOLDER_FILENAME in url:
        return True
    if "res.cloudinary.com" not in url:
        return True
    return False

class Command(BaseCommand):
    help = "Export properties and their image URLs to CSV. Use --only-missing to include only local/non-cloudinary entries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--out",
            "-o",
            default="property_images.csv",
            help="Output CSV file path (default: property_images.csv)",
        )
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only include properties with missing/local/non-Cloudinary image URLs",
        )

    def handle(self, *args, **options):
        out_path = options["out"]
        only_missing = options["only_missing"]

        fields = ("cover", "gallery1", "gallery2")
        rows_written = 0

        with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "title", "cover_url", "gallery1_url", "gallery2_url", "any_missing_or_local"])

            qs = Property.objects.all().order_by("id")
            for p in qs:
                urls = [get_url(getattr(p, f, None)) for f in fields]
                any_problem = any(looks_missing_or_local(u) for u in urls)

                if only_missing and not any_problem:
                    continue

                writer.writerow([p.pk, p.title, urls[0], urls[1], urls[2], "YES" if any_problem else "NO"])
                rows_written += 1

        self.stdout.write(self.style.SUCCESS(f"Wrote {rows_written} rows to {out_path}"))

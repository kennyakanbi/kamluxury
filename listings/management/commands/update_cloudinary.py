from django.core.management.base import BaseCommand
from listings.models import Property

class Command(BaseCommand):
    help = "Replace old /media/properties URLs with Cloudinary URLs"

    def handle(self, *args, **options):
        # Map the old file names or URL parts to Cloudinary URLs
        replacement = {
            "ech_3Ow83Xy.png": "https://res.cloudinary.com/<cloud_name>/image/upload/v<version>/ech_3Ow83Xy.png",
            "WhatsApp_Image_2025-10-15_at_06.03.59_51c1b15b.jpg": "https://res.cloudinary.com/<cloud_name>/image/upload/v<version>/WhatsApp_Image_2025-10-15_at_06.03.59_51c1b15b.jpg",
            "WhatsApp_Image_2025-10-02_at_10.29.35_e1793c10.jpg": "https://res.cloudinary.com/<cloud_name>/image/upload/v<version>/WhatsApp_Image_2025-10-02_at_10.29.35_e1793c10.jpg",
        }

        for p in Property.objects.all():
            updated = False
            for fname in ("cover", "gallery1", "gallery2"):
                f = getattr(p, fname)
                if f:
                    # Use the URL to detect old media
                    if f.url.startswith("/media/properties"):
                        # Extract file name from URL
                        file_name = f.url.split("/")[-1]
                        if file_name in replacement:
                            setattr(p, fname, replacement[file_name])
                            updated = True
            if updated:
                p.save()
                self.stdout.write(f"Updated Property {p.pk}: {p.title}")

        self.stdout.write(self.style.SUCCESS("Done updating Cloudinary URLs."))

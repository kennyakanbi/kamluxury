from django.core.management.base import BaseCommand
from listings.models import Property

PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/600x400.png?text=No+Image"

class Command(BaseCommand):
    help = "Replace missing property images with a placeholder"

    def handle(self, *args, **options):
        properties = Property.objects.all()
        for prop in properties:
            updated = False
            if not prop.cover:
                prop.cover = PLACEHOLDER_IMAGE_URL
                updated = True
            if not prop.gallery1:
                prop.gallery1 = PLACEHOLDER_IMAGE_URL
                updated = True
            if not prop.gallery2:
                prop.gallery2 = PLACEHOLDER_IMAGE_URL
                updated = True
            if updated:
                prop.save()
                self.stdout.write(self.style.SUCCESS(f"Updated {prop.title} with placeholder image(s)."))

        self.stdout.write(self.style.SUCCESS("Done updating missing images."))


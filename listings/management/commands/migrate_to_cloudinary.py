from django.core.management.base import BaseCommand
from listings.models import Property  # adjust to your actual model name
import cloudinary.uploader

class Command(BaseCommand):
    help = "Upload existing local property images to Cloudinary"

    def handle(self, *args, **options):
        properties = Property.objects.exclude(image='')
        for prop in properties:
            if not prop.image.url.startswith('http'):
                self.stdout.write(f"Uploading {prop.image.path}...")
                upload_result = cloudinary.uploader.upload(prop.image.path, folder='properties/')
                prop.image = upload_result['secure_url']
                prop.save()
                self.stdout.write(f"✅ Uploaded: {prop.image}")

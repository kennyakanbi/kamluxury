import os
from django.core.management.base import BaseCommand
from cloudinary.uploader import upload
from listings.models import Property  # ✅ correct import

class Command(BaseCommand):
    help = 'Upload existing Property images to Cloudinary'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        total = properties.count()
        print(f"Found {total} properties. Starting migration...")

        for index, prop in enumerate(properties, start=1):
            updated = False
            for field_name in ['cover', 'gallery1', 'gallery2']:
                field = getattr(prop, field_name)
                if field and not str(field).startswith('http'):
                    local_path = field.path if hasattr(field, 'path') else str(field)
                    if os.path.exists(local_path):
                        try:
                            result = upload(local_path, folder="properties")
                            setattr(prop, field_name, result['secure_url'])
                            updated = True
                            print(f"[{index}/{total}] Uploaded {field_name} for {prop.title}")
                        except Exception as e:
                            print(f"[{index}/{total}] Failed to upload {field_name} for {prop.title}: {e}")
                    else:
                        print(f"[{index}/{total}] File not found for {field_name} on {prop.title}: {local_path}")
            if updated:
                prop.save()

        print("Migration completed!")

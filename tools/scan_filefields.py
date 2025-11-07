# tools/scan_filefields.py
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.apps import apps

filenames = [
    "WhatsApp_Image_2025-10-15_at_06.03.59_51c1b15b.jpg",
    "WhatsApp_Image_2025-10-15_at_05.50.57_6044615e.jpg",
    "WhatsApp_Image_2025-10-15_at_05.52.21_cc98a74d.jpg",
    "ech_3Ow83Xy.png",
]

def scan():
    for fname in filenames:
        hits = []
        for model in apps.get_models():
            for field in model._meta.get_fields():
                field_name = getattr(field, "name", None)
                # look for FileField or ImageField (class name check works across migrations)
                if field.__class__.__name__ in ("FileField", "ImageField"):
                    qs = model.objects.all()[:5000]  # adjust if needed
                    for obj in qs:
                        f = getattr(obj, field_name, None)
                        if f:
                            name = getattr(f, "name", "")
                            url = getattr(f, "url", "")
                            if fname in name or fname in url:
                                hits.append((model.__name__, obj.pk, field_name, name, url))
        print(f"--- {fname} ({len(hits)} hits) ---")
        for h in hits:
            print(h)
    print("done")

if __name__ == "__main__":
    scan()

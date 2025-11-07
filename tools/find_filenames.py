# tools/find_filenames.py
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from listings.models import Property

filenames = [
    "WhatsApp_Image_2025-10-15_at_06.03.59_51c1b15b.jpg",
    "WhatsApp_Image_2025-10-15_at_05.50.57_6044615e.jpg",
    "WhatsApp_Image_2025-10-15_at_05.52.21_cc98a74d.jpg",
    "ech_3Ow83Xy.png",
    # add filenames you see in your logs
]

for fname in filenames:
    hits = []
    for p in Property.objects.all():
        for field in ("cover", "gallery1", "gallery2"):
            f = getattr(p, field, None)
            name = getattr(f, "name", None) if f else None
            url = getattr(f, "url", None) if f else None
            if name and fname in name:
                hits.append((p.pk, p.title, field, name, url))
            elif url and fname in url:
                hits.append((p.pk, p.title, field, name, url))
    print(f"--- {fname} ({len(hits)} hits) ---")
    for h in hits:
        print(h)

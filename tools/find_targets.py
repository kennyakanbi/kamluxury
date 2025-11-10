# tools/find_targets.py
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from listings.models import Property

targets = {
    "ech_3Ow83Xy.png",
    "WhatsApp_Image_2025-10-15_at_06.03.59_51c1b15b.jpg",
    "WhatsApp_Image_2025-10-02_at_10.29.35_e1793c10.jpg",
    "WhatsApp_Image_2025-09-22_at_08.52.07_5492b24b.jpg",
    "de_lekki_3_kAMmWiU.png",
}

found = []
for p in Property.objects.all():
    for fname in ("cover", "gallery1", "gallery2"):
        f = getattr(p, fname, None)
        if not f:
            continue
        name = getattr(f, "name", "") or ""
        url = getattr(f, "url", "") or ""
        for t in targets:
            if t in name or t in url:
                found.append({
                    "pk": p.pk,
                    "title": p.title,
                    "field": fname,
                    "name": name,
                    "url": url,
                })

if not found:
    print("No matches found in model image fields.")
else:
    print(f"Found {len(found)} matches:")
    for item in found:
        print(f"PK={item['pk']} FIELD={item['field']} NAME={item['name']!r} URL={item['url']!r} TITLE={item['title']!r}")

# tools/check_media_files.py
import os
from pathlib import Path
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django
django.setup()
from django.conf import settings
from listings.models import Property

MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", Path.cwd() / "media"))

print("MEDIA_ROOT:", MEDIA_ROOT)
missing = []
for p in Property.objects.all():
    for fname in ("cover","gallery1","gallery2"):
        f = getattr(p, fname, None)
        if not f:
            continue
        name = getattr(f, "name", None)
        url = getattr(f, "url", None) or ""
        # consider cloud host present if res.cloudinary.com in URL
        cloud = "res.cloudinary.com" in url
        path = MEDIA_ROOT / name if name else None
        exists = path.exists() if path else False
        print(f"PK={p.pk} FIELD={fname} name={name!r} cloud={cloud} exists_on_disk={exists} url={url!r}")
        if not cloud and not exists:
            missing.append((p.pk, fname, name, url))
print("\nMissing (non-cloud) files not found on disk:", len(missing))
for m in missing:
    print("  ", m)

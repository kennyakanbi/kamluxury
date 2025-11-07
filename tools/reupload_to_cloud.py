# tools/reupload_to_cloud.py
import os
from pathlib import Path
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django
django.setup()

from listings.models import Property
from django.conf import settings
from django.core.files import File

MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", Path.cwd() / "media"))
CLOUD_DOMAIN = "res.cloudinary.com"

def find_non_cloud_props():
    bad = []
    for p in Property.objects.all():
        for fname in ("cover","gallery1","gallery2"):
            f = getattr(p, fname, None)
            # treat empty file as (no file)
            if not f:
                continue
            url = getattr(f, "url", None) or ""
            name = getattr(f, "name", None)
            if CLOUD_DOMAIN not in url:
                bad.append((p.pk, p.title, fname, name, url))
    return bad

def try_reupload(item):
    pk, title, field_name, name, url = item
    p = Property.objects.get(pk=pk)
    f = getattr(p, field_name, None)
    if not f:
        return False, "field missing"
    name = getattr(f, "name", None)
    if not name:
        return False, "no saved name on field"
    local_path = MEDIA_ROOT / name
    if not local_path.exists():
        return False, f"local file not found at {local_path}"
    # open and save using default storage (Cloudinary)
    with open(local_path, "rb") as fh:
        django_file = File(fh)
        # Use save(name, File, save=True) to upload and persist
        getattr(p, field_name).save(os.path.basename(name), django_file, save=True)
    return True, "reuploaded/field saved"

if __name__ == "__main__":
    bad = find_non_cloud_props()
    print(f"Found {len(bad)} image fields without Cloudinary URLs.")
    if not bad:
        print("All good — no action needed.")
    else:
        for i, item in enumerate(bad, start=1):
            pk, title, fname, name, url = item
            print(f"{i}. PK={pk} FIELD={fname} NAME={name!r} URL={url!r} TITLE={title!r}")

        # how many to process in this run (safe default)
        N = 5
        print(f"\nAttempting reupload for up to {N} items (first {N}).\n")
        processed = 0
        for item in bad[:N]:
            success, msg = try_reupload(item)
            pk = item[0]
            print(f"PK={pk} => {success} : {msg}")
            processed += 1
        print(f"\nDone. Processed {processed} items. Re-run to process more.")

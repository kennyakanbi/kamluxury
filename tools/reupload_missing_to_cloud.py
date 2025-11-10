# tools/reupload_missing_to_cloud.py
"""
Find Property image fields that are stored locally under MEDIA_ROOT (paths like
/media/properties/...) and re-upload them using Django's default storage
(CloudinaryStorage in your settings). Run from project root:

PowerShell:
  $env:DJANGO_SETTINGS_MODULE="config.settings"
  python -m tools.reupload_missing_to_cloud

Or make the file self-contained (below already sets the env var if missing).
"""

import os
from pathlib import Path
import sys

# --- Ensure settings are configured BEFORE importing django models ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

# --- Now safe to import Django libs and your models ---
from django.conf import settings
from django.core.files import File
from listings.models import Property   # your app model
# ---------------------------------------------------------------

MEDIA_ROOT = Path(getattr(settings, "MEDIA_ROOT", Path.cwd() / "media"))
CLOUD_DOMAIN = "res.cloudinary.com"   # adjust if using a different cloud host

def find_non_cloud_props():
    bad = []
    for p in Property.objects.all():
        for fname in ("cover", "gallery1", "gallery2"):
            f = getattr(p, fname, None)
            # treat empty file as (no file)
            if not f:
                continue
            url = getattr(f, "url", None) or ""
            name = getattr(f, "name", None) or ""
            # If it's already a cloud URL skip it
            if CLOUD_DOMAIN in url:
                continue
            # if the storage url looks like a MEDIA path, consider it local and look on disk
            # Some storages return a path without leading slash; normalize for check
            if url.startswith("/media/") or "/media/properties" in name or "/media/properties" in url:
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
    # if name is something like 'properties/foo.jpg', MEDIA_ROOT / name works
    if not local_path.exists():
        return False, f"local file not found at {local_path}"
    # open and save using default storage (Cloudinary)
    try:
        with open(local_path, "rb") as fh:
            django_file = File(fh)
            # Use save(name, File, save=True) to upload and persist
            getattr(p, field_name).save(os.path.basename(name), django_file, save=True)
        return True, "reuploaded/field saved"
    except Exception as exc:
        return False, f"upload failed: {exc}"

def main():
    print(f"MEDIA_ROOT: {MEDIA_ROOT}")
    bad = find_non_cloud_props()
    print(f"Found {len(bad)} image fields that look local/not on Cloudinary.")
    if not bad:
        print("All good — no action needed.")
        return
    for i, item in enumerate(bad, start=1):
        pk, title, fname, name, url = item
        print(f"{i}. PK={pk} FIELD={fname} NAME={name!r} URL={url!r} TITLE={title!r}")

    # safe default: process N items so you can review
    N = 10
    print(f"\nAttempting reupload for up to {N} items (first {N}).\n")
    processed = 0
    for item in bad[:N]:
        success, msg = try_reupload(item)
        pk = item[0]
        print(f"PK={pk} => {success} : {msg}")
        processed += 1
    print(f"\nDone. Processed {processed} items. Re-run to process more.")

if __name__ == "__main__":
    main()

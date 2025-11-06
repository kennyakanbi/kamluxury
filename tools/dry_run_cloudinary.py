# tools/dry_run_cloudinary.py
# Usage (PowerShell):
#   $env:DJANGO_SETTINGS_MODULE="config.settings"
#   $env:CLOUDINARY_URL="cloudinary://<API_KEY>:<API_SECRET>@<CLOUD_NAME>"
#   python tools/dry_run_cloudinary.py
#
# Optionally set DATABASE_URL before running if you need to point at prod DB.

import os
import sys

# Ensure script runs from project root: adjust if needed
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Ensure DJANGO_SETTINGS_MODULE is set in the environment (we don't override it here)
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    print("ERROR: DJANGO_SETTINGS_MODULE not set. Example:")
    print('$env:DJANGO_SETTINGS_MODULE="config.settings"')
    sys.exit(1)

import django
django.setup()

from listings.models import Property

def is_cloudinary_url(url: str) -> bool:
    return bool(url and "res.cloudinary.com" in url)

def main(limit=None):
    qs = Property.objects.all().order_by("pk")
    if limit:
        qs = qs[:limit]

    media_root = getattr(__import__("django.conf").conf.settings, "MEDIA_ROOT",
                         os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media"))
    print(f"MEDIA_ROOT: {media_root!r}\n")

    total = 0
    skipped = 0
    would_upload = 0
    missing_files = 0

    for p in qs:
        total += 1
        cover = getattr(p, "cover", None)
        name = getattr(cover, "name", None) if cover else None
        url = getattr(cover, "url", None) if cover else None

        if not cover:
            print(f"ID:{p.pk:<3} TITLE:{p.title!r:50} FIELD:cover  -> (no file)")
            continue

        if is_cloudinary_url(url):
            skipped += 1
            print(f"ID:{p.pk:<3} TITLE:{p.title!r:50} SKIPPED (on Cloudinary) -> {url}")
            continue

        local_path = None
        if name:
            local_path = os.path.join(str(media_root), name)
        exists = os.path.exists(local_path) if local_path else False

        if exists:
            would_upload += 1
            print(f"ID:{p.pk:<3} TITLE:{p.title!r:50} WOULD UPLOAD -> name={name!r} local_path={local_path}")
        else:
            missing_files += 1
            print(f"ID:{p.pk:<3} TITLE:{p.title!r:50} MISSING    -> name={name!r} expected={local_path}")

    print("\nSummary:")
    print(f"  scanned: {total}")
    print(f"  skipped (already Cloudinary): {skipped}")
    print(f"  would upload (local file exists): {would_upload}")
    print(f"  missing local files: {missing_files}")

if __name__ == "__main__":
    # Optional: pass an integer limit via CLI args: python tools/dry_run_cloudinary.py 20
    lim = None
    if len(sys.argv) > 1:
        try:
            lim = int(sys.argv[1])
        except Exception:
            pass
    main(limit=lim)

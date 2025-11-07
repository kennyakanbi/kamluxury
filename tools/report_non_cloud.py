# tools/report_non_cloud.py
import os
import django

# make sure Django settings are available
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from listings.models import Property

def report():
    bad = []
    for p in Property.objects.all():
        for fname in ("cover", "gallery1", "gallery2"):
            f = getattr(p, fname, None)
            url = getattr(f, "url", None) or ""
            name = getattr(f, "name", None)
            if url and "res.cloudinary.com" not in url:
                bad.append((p.pk, p.title, fname, name, url))
            elif not url and name:
                bad.append((p.pk, p.title, fname, name, "<no url>"))

    if not bad:
        print(" All checked image fields have Cloudinary URLs (or are empty).")
    else:
        print("  Non-Cloudinary image fields found:")
        for item in bad:
            pk, title, field, name, url = item
            print(f"PK={pk} FIELD={field} NAME={name!r} URL={url!r} TITLE={title!r}")

if __name__ == "__main__":
    report()

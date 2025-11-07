# tools/print_images.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django
django.setup()
from listings.models import Property
from django.conf import settings

print("DEFAULT_FILE_STORAGE:", getattr(settings,'DEFAULT_FILE_STORAGE',None))
print("MEDIA_ROOT:", getattr(settings,'MEDIA_ROOT',None))
print("MEDIA_URL:", getattr(settings,'MEDIA_URL',None))
print("---- show first 10 property image fields ----")
for p in Property.objects.all()[:10]:
    cover = getattr(p, "cover", None)
    g1 = getattr(p, "gallery1", None)
    g2 = getattr(p, "gallery2", None)
    def info(f):
        if not f:
            return "(none)"
        return f"name={getattr(f,'name',None)!r} url={getattr(f,'url',None)!r}"
    print(f"PK={p.pk} TITLE={p.title!r}")
    print("  cover: ", info(cover))
    print("  gallery1:", info(g1))
    print("  gallery2:", info(g2))
    print("-"*60)

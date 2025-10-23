# save this as create_admin.py at your project root

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

if not User.objects.filter(username=ADMIN_USER).exists():
    User.objects.create_superuser(username=ADMIN_USER, email=ADMIN_EMAIL, password=ADMIN_PASS)
    print("Superuser created!")
else:
    user = User.objects.get(username=ADMIN_USER)
    user.set_password(ADMIN_PASS)
    user.save()
    print("Superuser password updated!")



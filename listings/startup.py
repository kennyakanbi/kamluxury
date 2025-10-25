from django.apps import apps
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

def create_admin_user():
    try:
        User = get_user_model()
        if settings.ADMIN_USER and not User.objects.filter(username=settings.ADMIN_USER).exists():
            User.objects.create_superuser(
                username=settings.ADMIN_USER,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASS
            )
            print(f"✅ Admin user '{settings.ADMIN_USER}' created successfully.")
    except (OperationalError, ProgrammingError):
        # DB not ready yet on first deploy
        pass

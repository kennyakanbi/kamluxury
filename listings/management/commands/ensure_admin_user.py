# listings/management/commands/ensure_admin_user.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create or update a staff/superuser from environment variables: ADMIN_USER, ADMIN_EMAIL, ADMIN_PASS."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USER")
        email = os.environ.get("ADMIN_EMAIL", "")
        password = os.environ.get("ADMIN_PASS")

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USER and ADMIN_PASS environment variables are required. Skipping admin creation."
            ))
            return

        user, created = User.objects.get_or_create(username=username, defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        })

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            if email:
                user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            changed = False
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if email and user.email != email:
                user.email = email
                changed = True
            # Always update password to match env var so you can rotate it via Render envs
            user.set_password(password)
            user.save()
            if changed:
                self.stdout.write(self.style.SUCCESS(f"Updated user '{username}' to staff/superuser and set password."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Set password for existing user '{username}'."))

# listings/management/commands/ensure_admin_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import sys

User = get_user_model()

class Command(BaseCommand):
    help = "Ensure a superuser exists. Uses ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD env vars."

    def handle(self, *args, **options):
        # read credentials from env (don't hardcode passwords)
        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        password = os.environ.get("ADMIN_PASSWORD")

        # If a superuser already exists, do nothing.
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Superuser already exists — skipping creation."))
            return

        # If no password provided, exit with a message (avoid creating weak default)
        if not password:
            self.stdout.write(self.style.ERROR(
                "ADMIN_PASSWORD not set — skipping auto-create. Set ADMIN_PASSWORD in your environment to enable auto creation."
            ))
            return

        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {username}"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to create superuser: {exc}"))
            # exit non-zero to make it obvious in logs if you prefer, but we won't exit to avoid breaking startup
            # sys.exit(1)

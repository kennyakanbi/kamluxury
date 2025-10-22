import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib import admin
try:
    from .models import Property, UnitOption, Lead
    HAS_UNITOPTION = True
except Exception:
    from .models import Property, Lead
    HAS_UNITOPTION = False

if HAS_UNITOPTION:
    class UnitOptionInline(admin.TabularInline):
        model = UnitOption
        extra = 1
else:
    UnitOptionInline = None

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "location", "is_featured", "created_at")
    search_fields = ("title", "location")
    if UnitOptionInline:
        inlines = [UnitOptionInline]

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "property", "created_at")
    search_fields = ("name", "phone", "property__title")

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

        if not created:
            updated = False
            if not user.is_staff:
                user.is_staff = True
                updated = True
            if not user.is_superuser:
                user.is_superuser = True
                updated = True
            if email and user.email != email:
                user.email = email
                updated = True
            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated existing user '{username}' to staff/superuser."))
        else:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))

        # Always ensure password (update if changed)
        if not created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Set password for '{username}'."))

# listings/admin.py
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

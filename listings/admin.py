from django.contrib import admin
from django.utils.html import format_html
from .models import Property, UnitOption, Lead

# --- Inline for UnitOption ---
class UnitOptionInline(admin.TabularInline):
    model = UnitOption
    extra = 1
    readonly_fields = ("unit_type_display",)

    def unit_type_display(self, obj):
        return obj.get_unit_type_display()
    unit_type_display.short_description = "Unit Type"

# --- Property Admin ---
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "location", "is_featured_badge", "created_at", "thumbnail_display")
    search_fields = ("title", "location")
    inlines = [UnitOptionInline]

    readonly_fields = ("cover_thumb", "gallery1_thumb", "gallery2_thumb")


    def thumbnail_display(self, obj):
        if obj.cover and hasattr(obj.cover, "url"):
            return format_html(
                '<img src="{}" width="60" style="object-fit: cover; border-radius: 4px;">',
                obj.cover.url
            )
        return "-"
    thumbnail_display.short_description = "Thumbnail"

    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: green; font-weight: bold;">Yes</span>')
        return "No"
    is_featured_badge.short_description = "Featured"

    def cover_thumb(self, obj):
        if obj.cover and hasattr(obj.cover, "url"):
            return format_html('<img src="{}" width="80" style="object-fit: cover; border-radius: 4px;">', obj.cover.url)
        return "-"
    cover_thumb.short_description = "Cover"

    def gallery1_thumb(self, obj):
        if obj.gallery1 and hasattr(obj.gallery1, "url"):
            return format_html('<img src="{}" width="80" style="object-fit: cover; border-radius: 4px;">', obj.gallery1.url)
        return "-"
    gallery1_thumb.short_description = "Gallery 1"

    def gallery2_thumb(self, obj):
        if obj.gallery2 and hasattr(obj.gallery2, "url"):
            return format_html('<img src="{}" width="80" style="object-fit: cover; border-radius: 4px;">', obj.gallery2.url)
        return "-"
    gallery2_thumb.short_description = "Gallery 2"

# --- Lead Admin ---
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "property", "option", "created_at")
    search_fields = ("name", "phone", "property__title", "option__label")
    list_filter = ("property", "created_at")

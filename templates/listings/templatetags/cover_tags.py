# listings/templatetags/cover_tags.py
from django import template
from django.templatetags.static import static
from cloudinary.utils import cloudinary_url
import cloudinary

register = template.Library()

@register.filter
def cover_url(obj_or_field, key=None):
    """
    Robustly resolve a cover image URL. Safe: won't raise if Cloudinary not configured.
    """
    try:
        # If a model instance plus a key was passed, try getattr(obj, key)
        if key and hasattr(obj_or_field, '__class__'):
            field = getattr(obj_or_field, key, None)
        else:
            field = obj_or_field

        if not field:
            return ''

        # Try storage-provided .url first
        try:
            url = field.url
            if url:
                return url
        except Exception:
            pass

        # If cloudinary is not configured, bail out (fallback handled by template)
        cfg = cloudinary.config()
        if not getattr(cfg, "cloud_name", None):
            # no cloud_name configured
            return ''

        # Try public_id attribute (CloudinaryField)
        public_id = getattr(field, 'public_id', None)
        if not public_id:
            s = str(field)
            if s and s.lower() not in ('none', 'null', ''):
                public_id = s

        if public_id:
            try:
                url, _ = cloudinary_url(public_id)
                return url
            except Exception:
                return ''

    except Exception:
        return ''

    return ''

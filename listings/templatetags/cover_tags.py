# listings/templatetags/cover_tags.py
from django import template
from django.templatetags.static import static
from django.utils.html import escape

register = template.Library()

@register.filter(name="cover_url")
def cover_url(obj, field_name="cover"):
    """
    Return a safe URL for an ImageField on the given object.
    Usage in template: {{ p|cover_url:"cover" }} or default field 'cover': {{ p|cover_url }}
    Logic:
      - If field is empty -> return placeholder static path
      - If field is a full URL (db stored secure_url) -> return it
      - If field is a FieldFile with .url -> try to use that (catch ValueError)
      - Otherwise return placeholder
    """
    placeholder = static("img/brand_1.png")  # change as desired

    # guard: obj may be a dict or model; try getattr
    try:
        if isinstance(field_name, str) and hasattr(obj, field_name):
            field = getattr(obj, field_name)
        else:
            # fallback: treat obj itself as the field/file
            field = obj
    except Exception:
        return placeholder

    # empty
    try:
        # If FieldFile with no file this will be falsy (''), or .name could be None
        name = getattr(field, "name", None)
        if not name:
            # if field is raw string that is empty, fallback
            # But maybe field is a direct URL string:
            if isinstance(field, str) and field.strip().startswith("http"):
                return field.strip()
            return placeholder
    except Exception:
        return placeholder

    # If it's already a URL-like string (e.g. you stored secure_url in DB)
    s = str(field)
    if s.startswith("http://") or s.startswith("https://"):
        return s

    # If FieldFile with .url, try to return it safely
    try:
        url = field.url
        # ensure we return a string
        return str(url)
    except ValueError:
        # no file associated
        return placeholder
    except Exception:
        # final fallback
        return placeholder

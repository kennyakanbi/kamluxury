# listings/validators.py
from django.core.exceptions import ValidationError

def validate_image_max_size(file_obj):
    """
    Raise ValidationError if file > 10MB.
    Attach this to model fields to block too-large uploads early.
    """
    max_bytes = 10 * 1024 * 1024  # 10 MB
    if not file_obj:
        return
    try:
        size = file_obj.size
    except AttributeError:
        return
    if size > max_bytes:
        raise ValidationError("File too large. Maximum file size is 10 MB.")

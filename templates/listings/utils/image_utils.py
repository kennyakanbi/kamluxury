from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def compress_image_file(uploaded_file, max_size_px=1600, quality=85, target_format="JPEG"):
    """
    Takes an InMemoryUploadedFile (from form/admin), resizes it preserving aspect ratio,
    re-encodes to target_format and returns a Django ContentFile ready to save to a FileField.
    """
    try:
        image = Image.open(uploaded_file)
    except Exception:
        return uploaded_file  # if not an image, return original

    # convert RGBA -> RGB to avoid save issues with JPEG
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # resize with thumbnail (preserve aspect ratio)
    image.thumbnail((max_size_px, max_size_px), Image.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format=target_format, quality=quality, optimize=True)
    buffer.seek(0)

    name = uploaded_file.name
    # ensure extension matches format
    if not name.lower().endswith(".jpg") and target_format.upper() == "JPEG":
        name = name.rsplit(".", 1)[0] + ".jpg"

    return ContentFile(buffer.read(), name=name)

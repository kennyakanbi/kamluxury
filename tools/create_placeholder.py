from PIL import Image, ImageDraw, ImageFont
import os

out_dir = os.path.join("static", "img")
os.makedirs(out_dir, exist_ok=True)
w, h = 600, 400
img = Image.new("RGB", (w, h), color=(220, 220, 220))
d = ImageDraw.Draw(img)
text = "No Image"

try:
    f = ImageFont.load_default()
except Exception:
    f = None

# compute text size using textbbox (Pillow ≥10)
bbox = d.textbbox((0, 0), text, font=f)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
d.text(((w - tw) / 2, (h - th) / 2), text, fill=(80, 80, 80), font=f)
out_path = os.path.join(out_dir, "placeholder_600x400.png")
img.save(out_path, "PNG")
print("✅ Saved:", out_path)

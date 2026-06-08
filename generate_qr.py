import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# ----------------------
# تنظیمات
# ----------------------
base_url = "https://parsia-restaurant.onrender.com/frontend/menu.html?table="
tables = 16
output_folder = "qrcodes"
logo_path = "logo.jpg"

os.makedirs(output_folder, exist_ok=True)

# بارگذاری لوگو
has_logo = False
try:
    logo = Image.open(logo_path).convert("RGBA")
    has_logo = True
    print(f"✅ Logo geladen: {logo_path}")
except Exception as e:
    print(f"⚠️ Logo Fehler: {e}")

for i in range(1, tables + 1):
    url = base_url + str(i)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    width, height = qr_img.size

    if has_logo:
        logo_size = int(width * 0.22)
        lw, lh = logo.size
        ratio = min(logo_size / lw, logo_size / lh)
        new_lw, new_lh = int(lw * ratio), int(lh * ratio)
        logo_resized = logo.resize((new_lw, new_lh), Image.LANCZOS)

        pad = 8
        logo_bg = Image.new("RGBA", (new_lw + pad*2, new_lh + pad*2), "white")
        logo_bg.paste(logo_resized, (pad, pad), logo_resized)

        pos = ((width - logo_bg.width) // 2, (height - logo_bg.height) // 2)
        qr_img.paste(logo_bg, pos)

    qr_rgb = qr_img.convert("RGB")
    new_height = height + 80
    final_img = Image.new("RGB", (width, new_height), "white")
    final_img.paste(qr_rgb, (0, 0))

    draw = ImageDraw.Draw(final_img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((width//2, height + 15), f"Tisch Nr. {i}", fill="black", font=font_large, anchor="mm")
    draw.text((width//2, height + 50), "Scannen Sie für die Speisekarte", fill="gray", font=font_small, anchor="mm")

    final_img.save(f"{output_folder}/Tisch_{i}_QR.png")
    print(f"✅ Tisch {i}")

print(f"\n✅ Alle {tables} QR Codes in '{output_folder}/'")

import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# ----------------------
# تنظیمات
# ----------------------
base_url = "https://parsiarestaurant.github.io/parsia-restaurant/frontend/menu.html?table="
tables = 16
output_folder = "qrcodes"

os.makedirs(output_folder, exist_ok=True)

for i in range(1, tables + 1):
    url = base_url + str(i)

    # ساخت QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # اضافه کردن متن
    width, height = qr_img.size
    new_height = height + 80
    final_img = Image.new("RGB", (width, new_height), "white")
    final_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final_img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text1 = f"Tisch Nr. {i}"
    text2 = "Scannen Sie für die Speisekarte"

    draw.text((width//2, height + 15), text1, fill="black", font=font_large, anchor="mm")
    draw.text((width//2, height + 50), text2, fill="gray",  font=font_small, anchor="mm")

    filename = f"{output_folder}/Tisch_{i}_QR.png"
    final_img.save(filename)
    print(f"✅ QR Code erstellt: Tisch {i}")

print(f"\n✅ Alle {tables} QR Codes im Ordner '{output_folder}/'")
print("Drucken Sie diese aus und legen Sie sie auf die Tische.")

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          Parsia Restaurant — Automatischer Bon-Drucker       ║
║          پارسیا رستوران — چاپگر خودکار سفارش‌ها             ║
╚══════════════════════════════════════════════════════════════╝

Dieses Skript läuft auf dem Laptop im Restaurant.
Es prüft alle paar Sekunden den Server auf neue Bestellungen
und druckt diese automatisch aus — der Gast sieht nichts davon.

روی لپتاپ رستوران اجرا کنید.
هر چند ثانیه سرور را چک می‌کند و سفارش جدید را چاپ می‌کند.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
نحوه نصب:
  pip install requests

نحوه اجرا:
  python parsia_printer.py

برای متوقف کردن: Ctrl+C
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import requests
import time
import os
import sys
import subprocess
import platform
import tempfile
from datetime import datetime

# ══════════════════════════════════════════════
#  تنظیمات / Einstellungen
# ══════════════════════════════════════════════

API_URL      = "https://parsia-restaurant.onrender.com"
CHECK_EVERY  = 8          # هر چند ثانیه چک شود (Sekunden)
PRINTER_NAME = ""         # خالی = چاپگر پیش‌فرض سیستم
                          # اگر چاپگر خاصی دارید اسمش را بنویسید
                          # z.B. "Epson TM-T20III"

# ══════════════════════════════════════════════
#  ثبت سفارش‌های چاپ‌شده (در حافظه)
# ══════════════════════════════════════════════
printed_orders = set()

# ══════════════════════════════════════════════
#  ساخت HTML برای چاپ
# ══════════════════════════════════════════════

def build_kitchen_html(order):
    """بون آشپزخانه — فقط نام غذا و تعداد، بزرگ و واضح"""
    now  = datetime.now().strftime("%d.%m.%Y %H:%M")
    rows = ""
    for item in order.get("items", []):
        rows += f"""
        <tr>
            <td style="font-size:22px;font-weight:bold;padding:8px 4px;border-bottom:1px dashed #aaa">
                {item['name']}
            </td>
            <td style="font-size:28px;font-weight:bold;text-align:center;padding:8px 4px;border-bottom:1px dashed #aaa">
                × {item['qty']}
            </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body   {{ font-family: 'Courier New', monospace; padding: 14px; margin: 0; }}
  h2     {{ text-align: center; font-size: 20px; margin-bottom: 4px; }}
  .meta  {{ text-align: center; font-size: 13px; margin-bottom: 10px; }}
  hr     {{ border: none; border-top: 2px dashed #333; margin: 8px 0; }}
  table  {{ width: 100%; border-collapse: collapse; }}
  @media print {{ @page {{ margin: 6mm; }} }}
</style>
</head>
<body>
  <h2>🍳 KÜCHE / آشپزخانه</h2>
  <div class="meta">
    <strong>Tisch: {order.get('table_number', '?')}</strong>
    &nbsp;|&nbsp; #{order.get('id', '')}
    <br>{now}
  </div>
  <hr>
  <table>{rows}</table>
  <hr>
</body>
</html>"""


def build_guest_html(order):
    """رسید مشتری — با قیمت و جمع کل"""
    now   = datetime.now().strftime("%d.%m.%Y %H:%M")
    rows  = ""
    total = 0.0
    for item in order.get("items", []):
        sub    = item["price"] * item["qty"]
        total += sub
        rows  += f"""
        <tr>
            <td style="padding:5px 3px;border-bottom:1px dashed #ccc">{item['name']}</td>
            <td style="text-align:center;padding:5px 3px;border-bottom:1px dashed #ccc">{item['qty']}</td>
            <td style="text-align:right;padding:5px 3px;border-bottom:1px dashed #ccc">{sub:.2f} €</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body   {{ font-family: 'Courier New', monospace; padding: 14px; margin: 0; font-size: 13px; }}
  h3     {{ text-align: center; font-size: 16px; margin-bottom: 4px; }}
  .meta  {{ text-align: center; margin-bottom: 10px; }}
  hr     {{ border: none; border-top: 1px dashed #555; margin: 8px 0; }}
  table  {{ width: 100%; border-collapse: collapse; }}
  th     {{ font-size: 11px; border-bottom: 2px solid #333; padding: 4px 3px; }}
  .total {{ font-weight: bold; font-size: 14px; border-top: 2px dashed #333; }}
  .foot  {{ text-align: center; margin-top: 12px; font-size: 12px; }}
  @media print {{ @page {{ margin: 6mm; }} }}
</style>
</head>
<body>
  <h3>🍴 Parsia Restaurant</h3>
  <div class="meta">
    {now}<br>
    Tisch Nr. <strong>{order.get('table_number', '?')}</strong>
  </div>
  <hr>
  <table>
    <tr>
      <th style="text-align:left">Artikel</th>
      <th>Menge</th>
      <th style="text-align:right">Preis</th>
    </tr>
    {rows}
    <tr class="total">
      <td colspan="2">GESAMT</td>
      <td style="text-align:right">{total:.2f} €</td>
    </tr>
  </table>
  <div class="foot">
    Bestellung #{order.get('id', '')}<br>
    MwSt. 19% inklusive<br><br>
    Vielen Dank für Ihren Besuch! 🙏<br>
    <small>سفارش شما ثبت شد ✦</small>
  </div>
</body>
</html>"""


# ══════════════════════════════════════════════
#  چاپ HTML
# ══════════════════════════════════════════════

def print_html(html_content, title="Bon"):
    """HTML را در یک فایل موقت ذخیره کرده و چاپ می‌کند"""
    # فایل موقت HTML
    with tempfile.NamedTemporaryFile(
        suffix=".html", mode="w", encoding="utf-8", delete=False
    ) as f:
        f.write(html_content)
        tmp_path = f.name

    system = platform.system()

    try:
        if system == "Windows":
            # ویندوز: از مرورگر پیش‌فرض استفاده می‌کند
            os.startfile(tmp_path, "print")
        elif system == "Darwin":
            # macOS
            subprocess.run(["open", "-a", "Safari", tmp_path], check=True)
        else:
            # Linux: با lp یا cups چاپ
            subprocess.run(
                ["lp", tmp_path] + (["-d", PRINTER_NAME] if PRINTER_NAME else []),
                check=True
            )
        time.sleep(2)  # کمی صبر کن تا چاپگر شروع کند
    except Exception as e:
        print(f"  ⚠️  Druckfehler / خطای چاپ: {e}")
        print(f"  ℹ️  Datei gespeichert / فایل ذخیره شد: {tmp_path}")
    finally:
        # پاک کردن فایل موقت (روی Windows با تاخیر)
        try:
            if system != "Windows":
                os.unlink(tmp_path)
        except Exception:
            pass


# ══════════════════════════════════════════════
#  چک کردن سرور
# ══════════════════════════════════════════════

def fetch_new_orders():
    """سفارش‌های جدید را از سرور می‌گیرد"""
    try:
        resp = requests.get(f"{API_URL}/orders", timeout=10)
        resp.raise_for_status()
        all_orders = resp.json()

        new_orders = []
        for order in all_orders:
            oid    = order.get("id")
            status = order.get("status", "")
            # فقط سفارش‌هایی که هنوز چاپ نشده و پرداخت نشده
            if oid and oid not in printed_orders and status != "paid":
                new_orders.append(order)

        return new_orders

    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  Keine Verbindung / اتصال نیست — {datetime.now().strftime('%H:%M:%S')}")
        return []
    except Exception as e:
        print(f"  ⚠️  Fehler: {e}")
        return []


def process_order(order):
    """یک سفارش جدید را پردازش و چاپ می‌کند"""
    oid   = order.get("id")
    table = order.get("table_number", "?")
    items = order.get("items", [])

    print(f"\n  ════════════════════════════════════")
    print(f"  🆕 Neue Bestellung / سفارش جدید!")
    print(f"     Tisch / میز: {table}  |  #{oid}")
    print(f"     Zeit / زمان: {datetime.now().strftime('%H:%M:%S')}")
    print(f"     Artikel / آیتم‌ها:")
    for item in items:
        print(f"       • {item['name']}  × {item['qty']}")

    print(f"\n  🖨️  Drucke Küchen-Bon... / چاپ بون آشپزخانه...")
    print_html(build_kitchen_html(order), title=f"Küche Tisch {table}")
    time.sleep(1)

    print(f"  🖨️  Drucke Gast-Bon... / چاپ رسید مشتری...")
    print_html(build_guest_html(order), title=f"Quittung Tisch {table}")

    printed_orders.add(oid)
    print(f"  ✅ Fertig! / انجام شد!")
    print(f"  ════════════════════════════════════")


# ══════════════════════════════════════════════
#  حلقه اصلی
# ══════════════════════════════════════════════

def main():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║    Parsia Restaurant — Bon-Drucker gestartet         ║")
    print("║    پارسیا رستوران — چاپگر روشن شد                   ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Server / سرور: {API_URL}")
    print(f"  Intervall / فاصله چک: alle {CHECK_EVERY} Sekunden")
    print(f"  Drucker / چاپگر: {'Standard / پیش‌فرض' if not PRINTER_NAME else PRINTER_NAME}")
    print(f"  Gestartet / شروع: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print()
    print("  Warte auf neue Bestellungen... / منتظر سفارش جدید...")
    print("  (Ctrl+C zum Beenden / برای خروج Ctrl+C بزنید)")
    print()

    while True:
        new_orders = fetch_new_orders()

        if new_orders:
            for order in new_orders:
                process_order(order)
        else:
            # فقط یک نقطه نمایش می‌دهیم که برنامه زنده است
            print(f"  · {datetime.now().strftime('%H:%M:%S')} — کانتینگ / Warte...", end="\r")

        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⛔ Beendet / متوقف شد. Auf Wiedersehen! خداحافظ!\n")
        sys.exit(0)

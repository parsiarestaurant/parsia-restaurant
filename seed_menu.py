import requests

API = "https://parsia-restaurant.onrender.com"
BASE = "https://raw.githubusercontent.com/parsiarestaurant/parsia-restaurant/main/frontend/images"

# ─── مسیرهای encode شده برای حروف خاص آلمانی ───
# Eintöpfe  → Eintoepfe
# Getränke  → Getraenke
# Heißegetränke → Hei%C3%9Fe%20Getraenke  (یا نام جدید پوشه)

menu_items = [
    # VORSPEISEN
    {"name": "Mirza Ghasemi",    "description": "Rauchige, gegrillte Auberginen mit Tomaten, Knoblauch und Ei · بادمجان کبابی با گوجه، سیر و تخم‌مرغ", "price": 7.90,  "category": "vorspeisen", "item_type": "food", "img_url": f"{BASE}/Vorspeisen/Mirza_Ghasemi.jpeg",    "active": True},
    {"name": "Kashke Bademjoon", "description": "Auberginen mit Röstzwiebeln, Walnüssen, Minze und Kashk · بادمجان با کشک، پیاز داغ و گردو",             "price": 7.50,  "category": "vorspeisen", "item_type": "food", "img_url": f"{BASE}/Vorspeisen/Kashke_Bademjoon.jpeg", "active": True},
    {"name": "Mast-o Khiar",     "description": "Joghurt-Dip mit Gurke und Minze · ماست با خیار و نعنا خشک",                                              "price": 5.50,  "category": "vorspeisen", "item_type": "food", "img_url": f"{BASE}/Vorspeisen/Mast-o_Khiar.jpeg",     "active": True},
    {"name": "Mast-o Moosir",    "description": "Joghurt-Dip mit Wildknoblauch · ماست با موسیر کوهی",                                                     "price": 5.50,  "category": "vorspeisen", "item_type": "food", "img_url": f"{BASE}/Vorspeisen/Mast-o_Moosir.jpeg",    "active": True},
    {"name": "Felafel",          "description": "Knusprige Kichererbsen-Bällchen mit Kräutern · فلافل ترد با سبزیجات و ادویه",                             "price": 5.50,  "category": "vorspeisen", "item_type": "food", "img_url": f"{BASE}/Vorspeisen/Felafel.jpeg",           "active": True},
    {"name": "Zeytoon Parvarde", "description": "Oliven in Walnuss-Granatapfel-Paste · زیتون با گردو، رب انار و سبزی",                                    "price": 5.50,  "category": "vorspeisen", "item_type": "food", "img_url": f"{BASE}/Vorspeisen/Zeytoon_Parvarde.jpeg", "active": True},

    # EINTOEPFE  (Eintöpfe → Eintoepfe)
    {"name": "Chelo Ghorme Sabzi",                   "description": "Kräutereintopf mit Lammfleisch, Kidneybohnen und Limetten · خورش سبزی با گوشت بره و لیمو عمانی",  "price": 14.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Chelo_Ghorme_Sabzi.jpeg",                    "active": True},
    {"name": "Chelo Ghormeh Sabzi (vegetarisch)",    "description": "Vegetarisch: Kräutereintopf mit Champignons · خورش سبزی گیاهی با قارچ و لیمو عمانی",              "price": 14.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Chelo_Ghormeh_Sabzi_vegetarisch.jpeg",    "active": True},
    {"name": "Chelo Khoresh Fesenjan",               "description": "Süß-saurer Eintopf mit Rinderhackfleisch, Walnüssen, Granatapfel · خورش فسنجان با گوشت چرخ‌کرده", "price": 18.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Chelo_Khoresh_Fesenjan.jpeg",               "active": True},
    {"name": "Chelo Khoresh Fesenjan (vegetarisch)", "description": "Vegetarisch: Süß-saurer Eintopf mit Walnüssen, Granatapfel · فسنجان گیاهی با گردو و رب انار",     "price": 18.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Chelo_Khoresh_Fesenjan_vegetarisch.jpeg", "active": True},
    {"name": "Baghali Polo Ba Mahiche",              "description": "Lammhaxe mit Dill-Safranreis und grünen Bohnen · ماهیچه با باقالی پلو و زعفران",                  "price": 22.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Baghali_Polo_Ba_Mahiche.jpeg",              "active": True},
    {"name": "Zereshk Polo Ba Morgh",                "description": "Hähnchenschenkel mit Berberitzen-Safranreis · مرغ با زرشک پلو و زعفران",                           "price": 19.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Zereshk_Polo_Ba_Morgh.jpeg",                "active": True},
    {"name": "Chelo Mahi",                           "description": "Gebratenes Fischfilet mit Safranreis oder grünen Bohnen · ماهی سرخ‌شده با برنج زعفرانی",           "price": 22.90, "category": "eintoepfe", "item_type": "food", "img_url": f"{BASE}/Eintoepfe/Chelo_Mahi.jpeg",                           "active": True},

    # GRILL
    {"name": "Chelo Kabab Koobideh", "description": "Zwei Spieße Lamm- und Rinderhackfleisch, gegrillt · دو سیخ کباب کوبیده با برنج زعفرانی", "price": 18.50, "category": "grill", "item_type": "food", "img_url": f"{BASE}/Gegrilltes/Chelo_Kabab_Koobideh.jpeg", "active": True},
    {"name": "Chelo Kabab Barg",     "description": "Zartes mariniertes Lammfilet in Streifen · فیله بره مرینیت‌شده با برنج زعفرانی",           "price": 24.50, "category": "grill", "item_type": "food", "img_url": f"{BASE}/Gegrilltes/Chelo_Kabab_Barg.jpeg",     "active": True},
    {"name": "Chelo Joojeh Kabab",   "description": "Mariniertes Hähnchenfleisch in Safran · جوجه کباب زعفرانی با برنج",                        "price": 19.50, "category": "grill", "item_type": "food", "img_url": f"{BASE}/Gegrilltes/Chelo_Joojeh_Kabab.jpeg",   "active": True},
    {"name": "Chelo Kabab Soltani",  "description": "Königsplatte: Koobideh und Barg Spieß · ترکیب کباب کوبیده و برگ با برنج زعفرانی",         "price": 29.50, "category": "grill", "item_type": "food", "img_url": f"{BASE}/Gegrilltes/Chelo_Kabab_Soltani.jpeg",  "active": True},

    # DESSERTS
    {"name": "Bastani Sonati", "description": "Traditionelles iranisches Safraneis mit Pistazie · بستنی زعفرانی سنتی ایرانی با پسته", "price": 5.00, "category": "desserts", "item_type": "food", "img_url": f"{BASE}/Desserts/Bastani_Sonati.jpeg", "active": True},
    {"name": "Tiramisu",       "description": "Klassisches italienisches Tiramisu · تیرامیسوی کلاسیک ایتالیایی",                       "price": 5.00, "category": "desserts", "item_type": "food", "img_url": f"{BASE}/Desserts/Tiramisu.jpeg",       "active": True},
    {"name": "Baklava",        "description": "Zwei frische Pistazien-Baklava mit Chai · دو تکه باقلوای تازه پسته‌ای با چای",          "price": 6.00, "category": "desserts", "item_type": "food", "img_url": f"{BASE}/Desserts/Baklava.jpeg",        "active": True},

    # GETRAENKE  (Getränke → Getraenke)
    {"name": "Doogh 0.2L",      "description": "Persischer Joghurt-Drink · نوشیدنی ماستی ایرانی",              "price": 3.00, "category": "getraenke", "item_type": "drink", "img_url": f"{BASE}/Getraenke/Doogh_0.2L.jpg",       "active": True},
    {"name": "Doogh 0.4L",      "description": "Persischer Joghurt-Drink · نوشیدنی ماستی ایرانی",              "price": 4.00, "category": "getraenke", "item_type": "drink", "img_url": f"{BASE}/Getraenke/Doogh_0.4L.jpg",       "active": True},
    {"name": "Softdrinks 0.2L", "description": "Cola, Cola Zero, Sprite, Fanta, Spezi, Apfelschorle",           "price": 2.40, "category": "getraenke", "item_type": "drink", "img_url": f"{BASE}/Getraenke/Softdrinks_0.2L.jpg",  "active": True},
    {"name": "Softdrinks 0.4L", "description": "Cola, Cola Zero, Sprite, Fanta, Spezi, Apfelschorle",           "price": 4.00, "category": "getraenke", "item_type": "drink", "img_url": f"{BASE}/Getraenke/Softdrinks_0.4L.jpg",  "active": True},
    {"name": "Wasser 0.25L",    "description": "Still oder Sprudel · آب معدنی ساده یا گازدار",                  "price": 2.50, "category": "getraenke", "item_type": "drink", "img_url": f"{BASE}/Getraenke/Wasser_0.25L.jpg",     "active": True},
    {"name": "Wasser 0.75L",    "description": "Still oder Sprudel · آب معدنی ساده یا گازدار",                  "price": 6.50, "category": "getraenke", "item_type": "drink", "img_url": f"{BASE}/Getraenke/Wasser_0.75L.jpg",   "active": True},

    # HEISSE GETRAENKE  (HeißeGetränke → Hei%C3%9FeGetraenke)
    {"name": "Kaffee",                       "description": "Frisch gebrühter Kaffee · قهوه تازه‌دم",                      "price": 2.50, "category": "heisse", "item_type": "drink", "img_url": f"{BASE}/HeisseGetraenke/Kaffee.jpg",                    "active": True},
    {"name": "Espresso",                     "description": "Klassischer Espresso · اسپرسوی کلاسیک",                        "price": 2.50, "category": "heisse", "item_type": "drink", "img_url": f"{BASE}/HeisseGetraenke/Espresso.jpg",                  "active": True},
    {"name": "Chai – Persischer Schwarztee", "description": "Traditioneller iranischer Schwarztee · چای سیاه سنتی ایرانی", "price": 2.00, "category": "heisse", "item_type": "drink", "img_url": f"{BASE}/HeisseGetraenke/Chai_Persischer_Schwarztee.jpg", "active": True},
]

# ─── ابتدا همه آیتم‌های قدیمی را پاک کن ───
print("🗑️  در حال پاک کردن آیتم‌های قدیمی...")
try:
    existing = requests.get(f"{API}/admin/menu", timeout=30).json()
    for item in existing:
        requests.delete(f"{API}/admin/menu/{item['id']}", timeout=10)
    print(f"✅ {len(existing)} آیتم قدیمی پاک شد\n")
except Exception as e:
    print(f"⚠️  نتوانستم آیتم‌های قدیمی را پاک کنم: {e}\n")

# ─── آیتم‌های جدید را اضافه کن ───
print(f"در حال اضافه کردن {len(menu_items)} آیتم به دیتابیس...\n")

success = 0
failed = 0

for item in menu_items:
    try:
        r = requests.post(f"{API}/admin/menu", json=item, timeout=30)
        if r.status_code == 200:
            print(f"✅ {item['name']}")
            success += 1
        else:
            print(f"❌ {item['name']} — {r.status_code}: {r.text}")
            failed += 1
    except Exception as e:
        print(f"❌ {item['name']} — خطا: {e}")
        failed += 1

print(f"\n✅ موفق: {success}  |  ❌ ناموفق: {failed}")

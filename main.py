from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import json
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Restaurant API is running ✅"}

# ──────────────────────────────────────────
# MENU ITEMS API
# ──────────────────────────────────────────

@app.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    """همه آیتم‌های فعال منو — برای مشتری و گارسون"""
    items = db.query(database.MenuItem).filter(database.MenuItem.active == True).all()
    return [_item_dict(i) for i in items]

@app.get("/admin/menu")
def get_all_menu(db: Session = Depends(get_db)):
    """همه آیتم‌ها شامل غیرفعال — فقط برای پنل مدیریت"""
    items = db.query(database.MenuItem).all()
    return [_item_dict(i) for i in items]

@app.post("/admin/menu")
def add_menu_item(data: dict, db: Session = Depends(get_db)):
    item = database.MenuItem(
        name        = data["name"],
        description = data.get("description", ""),
        price       = float(data["price"]),
        category    = data["category"],
        item_type   = data.get("item_type", "food"),
        img_url     = data.get("img_url", ""),
        active      = data.get("active", True),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "✅ Artikel hinzugefügt", "item": _item_dict(item)}

@app.put("/admin/menu/{item_id}")
def update_menu_item(item_id: int, data: dict, db: Session = Depends(get_db)):
    item = db.query(database.MenuItem).filter(database.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    for field in ["name", "description", "price", "category", "item_type", "img_url", "active"]:
        if field in data:
            setattr(item, field, data[field])
    db.commit()
    db.refresh(item)
    return {"message": "✅ Aktualisiert", "item": _item_dict(item)}

@app.delete("/admin/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(database.MenuItem).filter(database.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    db.delete(item)
    db.commit()
    return {"message": "✅ Gelöscht"}

def _item_dict(item):
    return {
        "id":          item.id,
        "name":        item.name,
        "description": item.description,
        "price":       item.price,
        "category":    item.category,
        "item_type":   item.item_type,
        "img_url":     item.img_url,
        "active":      item.active,
    }

# ──────────────────────────────────────────
# ORDERS API
# ──────────────────────────────────────────

@app.post("/orders")
def create_order(order: dict, db: Session = Depends(get_db)):
    items_json = json.dumps(order["items"], ensure_ascii=False)
    total = 0.0
    for item in order["items"]:
        total += item.get("price", 0) * item.get("qty", 1)
    new_order = database.Order(
        table_number = order["table"],
        items        = items_json,
        status       = "pending",
        total        = round(total, 2),
        created_at   = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        archived     = False,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {
        "message":    "Order saved ✅",
        "order_id":   new_order.id,
        "table":      new_order.table_number,
        "total":      new_order.total,
        "created_at": new_order.created_at
    }

@app.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    date: str = Query(None, description="فیلتر تاریخ: YYYY-MM-DD"),
    date_from: str = Query(None, description="از تاریخ: YYYY-MM-DD"),
    date_to: str = Query(None, description="تا تاریخ: YYYY-MM-DD"),
    status: str = Query(None, description="فیلتر وضعیت: pending / paid"),
    include_archived: bool = Query(False, description="نمایش بایگانی‌شده‌ها"),
):
    """
    دریافت سفارش‌ها با فیلترهای اختیاری:
    - ?date=2026-05-29          → فقط سفارش‌های آن روز
    - ?date_from=2026-05-01&date_to=2026-05-31  → بازه تاریخ
    - ?status=pending           → فقط سفارش‌های در انتظار
    - ?include_archived=true    → شامل بایگانی‌شده‌ها (برای گزارش مالیاتی)
    """
    q = db.query(database.Order)

    # فیلتر بایگانی — به‌صورت پیش‌فرض بایگانی‌شده‌ها نمایش داده نمی‌شوند
    if not include_archived:
        q = q.filter(
            (database.Order.archived == False) | (database.Order.archived == None)
        )

    # فیلتر تاریخ دقیق
    if date:
        q = q.filter(database.Order.created_at.like(f"{date}%"))

    # فیلتر بازه تاریخ
    if date_from:
        q = q.filter(database.Order.created_at >= f"{date_from} 00:00:00")
    if date_to:
        q = q.filter(database.Order.created_at <= f"{date_to} 23:59:59")

    # فیلتر وضعیت
    if status:
        q = q.filter(database.Order.status == status)

    orders = q.order_by(database.Order.id.desc()).all()
    return [parse_order(o) for o in orders]


@app.get("/orders/summary")
def get_orders_summary(
    db: Session = Depends(get_db),
    date: str = Query(None, description="تاریخ: YYYY-MM-DD (پیش‌فرض: امروز)"),
    date_from: str = Query(None, description="از تاریخ برای گزارش هفتگی/ماهانه"),
    date_to: str = Query(None, description="تا تاریخ"),
):
    """
    گزارش روزانه / هفتگی / ماهانه برای Tagesübersicht
    شامل: مجموع درآمد، تعداد سفارش، تفکیک نقدی/کارت
    """
    if not date and not date_from:
        date = datetime.now().strftime("%Y-%m-%d")

    q = db.query(database.Order).filter(database.Order.status == "paid")

    if date:
        q = q.filter(database.Order.created_at.like(f"{date}%"))
    if date_from:
        q = q.filter(database.Order.created_at >= f"{date_from} 00:00:00")
    if date_to:
        q = q.filter(database.Order.created_at <= f"{date_to} 23:59:59")

    paid_orders = q.all()
    parsed = [parse_order(o) for o in paid_orders]

    total_revenue = sum(o["total"] or 0 for o in parsed)
    bar_revenue   = sum(o["total"] or 0 for o in parsed if o.get("paymentMethod") == "bar")
    karte_revenue = sum(o["total"] or 0 for o in parsed if o.get("paymentMethod") == "karte")
    unique_tables = len(set(o["table_number"] for o in parsed))
    avg_per_table = round(total_revenue / unique_tables, 2) if unique_tables else 0

    # همه سفارش‌های روز (شامل pending)
    q_all = db.query(database.Order)
    if date:
        q_all = q_all.filter(database.Order.created_at.like(f"{date}%"))
    if date_from:
        q_all = q_all.filter(database.Order.created_at >= f"{date_from} 00:00:00")
    if date_to:
        q_all = q_all.filter(database.Order.created_at <= f"{date_to} 23:59:59")

    all_day_orders = q_all.filter(
        (database.Order.archived == False) | (database.Order.archived == None)
    ).all()

    return {
        "date":           date or f"{date_from} → {date_to}",
        "total_revenue":  round(total_revenue, 2),
        "bar_revenue":    round(bar_revenue, 2),
        "karte_revenue":  round(karte_revenue, 2),
        "paid_count":     len(paid_orders),
        "total_count":    len(all_day_orders),
        "pending_count":  sum(1 for o in all_day_orders if o.status == "pending"),
        "unique_tables":  unique_tables,
        "avg_per_table":  avg_per_table,
    }


@app.get("/kitchen")
def kitchen_orders(db: Session = Depends(get_db)):
    orders = db.query(database.Order).filter(
        database.Order.status == "pending",
        (database.Order.archived == False) | (database.Order.archived == None)
    ).all()
    return [parse_order(o) for o in orders]


@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    return parse_order(order)


@app.put("/orders/{order_id}")
def update_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    if "status" in data:
        order.status = data["status"]
    if "items" in data:
        order.items = json.dumps(data["items"], ensure_ascii=False)
    if "total" in data:
        order.total = round(data["total"], 2)
    if "paymentMethod" in data:
        try:
            items = json.loads(order.items)
        except:
            items = []
        items_clean = [i for i in items if not i.get("_meta")]
        items_clean.append({"_meta": True, "paymentMethod": data["paymentMethod"]})
        order.items = json.dumps(items_clean, ensure_ascii=False)
    db.commit()
    db.refresh(order)
    return {"message": "Updated ✅", "order": parse_order(order)}


@app.put("/orders/{order_id}/archive")
def archive_order(order_id: int, db: Session = Depends(get_db)):
    """
    بایگانی سفارش — جایگزین حذف.
    سفارش در دیتابیس باقی می‌ماند (برای گزارش مالیاتی Finanzamt)
    اما در داشبورد روزانه نمایش داده نمی‌شود.
    """
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.archived    = True
    order.archived_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.commit()
    return {"message": "Archiviert ✅", "order_id": order_id, "archived_at": order.archived_at}


@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """
    ⚠️ Hard-delete — فقط برای تست / توسعه استفاده شود.
    در محیط production از PUT /orders/{id}/archive استفاده کنید.
    """
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    db.delete(order)
    db.commit()
    return {"message": "Deleted ✅"}


@app.delete("/orders")
def delete_all_orders(db: Session = Depends(get_db)):
    """⚠️ فقط برای تست — همه سفارش‌ها را حذف می‌کند"""
    count = db.query(database.Order).delete()
    db.commit()
    return {"message": f"Alle {count} Bestellungen gelöscht ✅"}


def parse_order(order):
    try:
        raw = json.loads(order.items)
    except:
        raw = []
    items = [i for i in raw if not i.get("_meta")]
    meta  = next((i for i in raw if i.get("_meta")), {})
    return {
        "id":            order.id,
        "table_number":  order.table_number,
        "items":         items,
        "status":        order.status,
        "total":         order.total,
        "created_at":    order.created_at,
        "paymentMethod": meta.get("paymentMethod", None),
        "archived":      order.archived or False,
        "archived_at":   order.archived_at,
    }

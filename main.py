from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import json
from datetime import datetime

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
# MENU ITEMS API  (مدیریت منو توسط مالک)
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
    """اضافه کردن آیتم جدید به منو"""
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
    """ویرایش آیتم موجود"""
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
    """حذف آیتم از منو"""
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
        created_at   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(database.Order).all()
    return [parse_order(o) for o in orders]

@app.get("/kitchen")
def kitchen_orders(db: Session = Depends(get_db)):
    orders = db.query(database.Order).filter(database.Order.status == "pending").all()
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

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    db.delete(order)
    db.commit()
    return {"message": "Deleted ✅"}

@app.delete("/orders")
def delete_all_orders(db: Session = Depends(get_db)):
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
        "paymentMethod": meta.get("paymentMethod", None)
    }

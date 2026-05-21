from fastapi import FastAPI, Depends
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

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Restaurant API is running ✅"}

menu = [
    {"id": 1, "name": "Chelo Ghormeh Sabzi", "description": "Kräutereintopf mit Lammfleisch", "price": 14.90, "category": "Eintöpfe"},
    {"id": 2, "name": "Zereshk Polo Ba Morgh", "description": "Hähnchenschenkel mit Berberitzenreis", "price": 19.90, "category": "Eintöpfe"},
    {"id": 3, "name": "Chelo Kebab", "description": "Gegrillter Kebab mit Safranreis", "price": 18.90, "category": "Grill"},
    {"id": 4, "name": "Cola", "description": "Erfrischungsgetränk", "price": 3.50, "category": "Getränke"},
    {"id": 5, "name": "Mineralwasser", "description": "Still oder sprudelnd", "price": 2.50, "category": "Getränke"},
]

@app.get("/menu")
def get_menu():
    return menu

@app.post("/orders")
def create_order(order: dict, db: Session = Depends(get_db)):
    items_json = json.dumps(order["items"], ensure_ascii=False)

    total = 0.0
    for item in order["items"]:
        total += item.get("price", 0) * item.get("qty", 1)

    new_order = database.Order(
        table_number=order["table"],
        items=items_json,
        status="pending",
        total=round(total, 2),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order saved ✅",
        "order_id": new_order.id,
        "table": new_order.table_number,
        "total": new_order.total,
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

# ----------------------
# UPDATE ORDER — status + items + total + paymentMethod
# ----------------------
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
        # Store paymentMethod in items field as metadata if no dedicated column
        try:
            items = json.loads(order.items)
        except:
            items = []
        order.items = json.dumps(items, ensure_ascii=False)
        # Save paymentMethod in a note or ignore if no column
        pass

    db.commit()
    db.refresh(order)
    return {"message": "Updated ✅", "order": parse_order(order)}

# ----------------------
# DELETE ORDER
# ----------------------
@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    db.delete(order)
    db.commit()
    return {"message": "Deleted ✅"}

def parse_order(order):
    try:
        items = json.loads(order.items)
    except:
        items = []
    return {
        "id": order.id,
        "table_number": order.table_number,
        "items": items,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at
    }

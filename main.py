from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import json
from datetime import datetime

app = FastAPI()

# ----------------------
# CORS - allow all origins for local dev
# ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# SERVE FRONTEND FILES
# ----------------------
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ----------------------
# DATABASE SESSION
# ----------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# HOME
# ----------------------
@app.get("/")
def home():
    return {"message": "Restaurant API is running ✅"}

# ----------------------
# MENU
# ----------------------
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

# ----------------------
# CREATE ORDER
# ----------------------
@app.post("/orders")
def create_order(order: dict, db: Session = Depends(get_db)):
    items_json = json.dumps(order["items"], ensure_ascii=False)
    
    # Calculate total
    total = 0.0
    for item in order["items"]:
        total += item.get("price", 0) * item.get("qty", 1)

    new_order = database.Order(
        table_number=order["table"],
        items=items_json,          # ✅ FIX: save as JSON string
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

# ----------------------
# GET ALL ORDERS
# ----------------------
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(database.Order).all()
    return [parse_order(o) for o in orders]

# ----------------------
# KITCHEN - pending only
# ----------------------
@app.get("/kitchen")
def kitchen_orders(db: Session = Depends(get_db)):
    orders = db.query(database.Order).filter(database.Order.status == "pending").all()
    return [parse_order(o) for o in orders]

# ----------------------
# GET SINGLE ORDER (for receipt)
# ----------------------
@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    return parse_order(order)

# ----------------------
# UPDATE ORDER STATUS
# ----------------------
@app.put("/orders/{order_id}")
def update_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.id == order_id).first()
    if not order:
        return {"message": "Order not found"}
    order.status = data["status"]
    db.commit()
    db.refresh(order)
    return {"message": "Updated ✅", "order": parse_order(order)}

# ----------------------
# HELPER: parse order items from JSON string
# ----------------------
def parse_order(order):
    try:
        items = json.loads(order.items)
    except:
        items = []
    return {
        "id": order.id,
        "table_number": order.table_number,   # ✅ FIX: consistent field name
        "items": items,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at
    }

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Index
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------
# DATABASE CONNECTION
# ----------------------
import os
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///restaurant.db")
# Render PostgreSQL URL starts with postgres:// — fix for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ----------------------
# ORDER TABLE MODEL
# ----------------------
class Order(Base):
    __tablename__ = "orders"

    id           = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer)
    items        = Column(String)          # JSON string
    status       = Column(String)          # pending / ready / paid
    total        = Column(Float, default=0.0)
    created_at   = Column(String, index=True)   # ایندکس برای فیلتر سریع تاریخ

    # ── Soft-delete: سفارش‌ها هیچ‌گاه حذف نمی‌شوند (برای گزارش مالیاتی) ──
    archived     = Column(Boolean, default=False)  # True = بایگانی‌شده (نه حذف‌شده)
    archived_at  = Column(String, nullable=True)   # زمان بایگانی

# ----------------------
# MENU ITEM TABLE MODEL
# ----------------------
class MenuItem(Base):
    __tablename__ = "menu_items"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    description = Column(String, default="")
    price       = Column(Float, nullable=False)
    category    = Column(String, nullable=False)   # vorspeisen / eintoepfe / grill / desserts / getraenke / heisse
    item_type   = Column(String, default="food")   # food / drink
    img_url     = Column(String, default="")       # URL عکس
    active      = Column(Boolean, default=True)    # نمایش یا پنهان


# ----------------------
# EXPENSE TABLE MODEL
# ----------------------
class Expense(Base):
    __tablename__ = "expenses"

    id          = Column(Integer, primary_key=True, index=True)
    date        = Column(String, nullable=False, index=True)   # YYYY-MM-DD
    description = Column(String, nullable=False)
    amount      = Column(Float, nullable=False)
    category    = Column(String, default="Sonstiges")  # Lebensmittel / Getränke / Reinigung / Personal / Sonstiges
    created_by      = Column(String, default="Inhaber")
    created_at      = Column(String)
    receipt_number  = Column(String, nullable=True)   # شماره رسید

# ----------------------
# SETTINGS TABLE MODEL
# ----------------------
class Setting(Base):
    __tablename__ = "settings"

    key   = Column(String, primary_key=True)
    value = Column(String, nullable=False)

# ----------------------
# CREATE TABLES
# ----------------------
Base.metadata.create_all(bind=engine)

# ── Initialize default settings after table creation ──
def init_defaults():
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    try:
        existing = db.query(Setting).filter(Setting.key == "owner_pin").first()
        if not existing:
            db.add(Setting(key="owner_pin", value="0000"))
            db.commit()
            print("✅ Default PIN initialized")
    except Exception as e:
        print(f"⚠️ init_defaults: {e}")
    finally:
        db.close()

init_defaults()

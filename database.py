from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Index
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------
# DATABASE CONNECTION
# ----------------------
engine = create_engine("sqlite:///restaurant.db", connect_args={"check_same_thread": False})

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
    created_by  = Column(String, default="Inhaber")
    created_at  = Column(String)

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

# ── Migration: اگر ستون‌های جدید در دیتابیس قدیمی وجود ندارند، اضافه کن ──
def run_migrations():
    import sqlite3
    conn = sqlite3.connect("restaurant.db")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(orders)")
    existing_cols = {row[1] for row in cur.fetchall()}

    if "archived" not in existing_cols:
        cur.execute("ALTER TABLE orders ADD COLUMN archived BOOLEAN DEFAULT 0")
        print("✅ Migration: 'archived' column added")

    if "archived_at" not in existing_cols:
        cur.execute("ALTER TABLE orders ADD COLUMN archived_at TEXT")
        print("✅ Migration: 'archived_at' column added")

    # Expenses table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
    if not cur.fetchone():
        cur.execute("""CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT DEFAULT 'Sonstiges',
            created_by TEXT DEFAULT 'Inhaber',
            created_at TEXT
        )""")
        print("✅ Migration: 'expenses' table created")

    # Settings table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
    if not cur.fetchone():
        cur.execute("""CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )""")
        cur.execute("INSERT INTO settings (key, value) VALUES ('owner_pin', '0000')")
        print("✅ Migration: 'settings' table created with default PIN")

    conn.commit()
    conn.close()

run_migrations()

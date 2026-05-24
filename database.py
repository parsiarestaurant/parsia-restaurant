from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
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
    created_at   = Column(String)

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
# CREATE TABLES
# ----------------------
Base.metadata.create_all(bind=engine)

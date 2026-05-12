from sqlalchemy import create_engine, Column, Integer, String, Float
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

    id         = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer)
    items      = Column(String)          # JSON string
    status     = Column(String)          # pending / ready / paid
    total      = Column(Float, default=0.0)   # ✅ NEW: total price
    created_at = Column(String)               # ✅ NEW: timestamp

# ----------------------
# CREATE TABLES
# ----------------------
Base.metadata.create_all(bind=engine)

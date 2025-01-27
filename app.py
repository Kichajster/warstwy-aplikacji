from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Inicjalizacja aplikacji FastAPI
app = FastAPI()

# Konfiguracja bazy danych SQLite
DATABASE_URL = "sqlite:///./products.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Model bazy danych
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)

# Tworzenie tabeli w bazie danych
Base.metadata.create_all(bind=engine)

# Model danych do API
class ProductCreate(BaseModel):
    name: str
    description: str
    price: int

class ProductResponse(ProductCreate):
    id: int

    class Config:
        orm_mode = True

# Endpointy API
@app.get("/products", response_model=List[ProductResponse])
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(name=product.name, description=product.description, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    db.close()
    return {"detail": "Product deleted"}

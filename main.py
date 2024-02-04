from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class User(UserCreate):
    id: int


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float


class Product(ProductCreate):
    id: int


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    status: str


class Order(OrderCreate):
    id: int
    order_date: datetime


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Integer)


class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('pending', 'completed', 'cancelled'), default='pending')


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserDB(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = ProductDB(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = OrderDB(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "datamart"}  # Add schema specification
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "datamart"}  # Add schema specification
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "datamart"}  # Add schema specification
    id = Column(Integer, primary_key=True)
    customer_id = Column(
        Integer, ForeignKey("datamart.customers.id"), nullable=False
    )  # Include schema with FK
    order_date = Column(DateTime, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "datamart"}  # Add schema specification
    id = Column(Integer, primary_key=True)
    order_id = Column(
        Integer, ForeignKey("datamart.orders.id"), nullable=False
    )  # Include schema with FK
    product_id = Column(Integer, ForeignKey("datamart.products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

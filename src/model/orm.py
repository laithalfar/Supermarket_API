from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from datetime import date, time
from decimal import Decimal
from src.database import Base

class Customer(Base):
    __tablename__ = "CUSTOMERS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    membership: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False, default="password123")

    transactions = relationship("Transaction", back_populates="customer")

class Branch(Base):
    __tablename__ = "BRANCHES"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=0)
    total_stock: Mapped[int] = mapped_column(Integer, default=0)

    transactions = relationship("Transaction", back_populates="branch")

class Employee(Base):
    __tablename__ = "EMPLOYEES"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    dateOfEmployment: Mapped[date] = mapped_column(Date, nullable=True)
    dateOfEndOfEmployment: Mapped[Optional[date]] = mapped_column(Date, default=None, nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False, default="password123")

class Product(Base):
    __tablename__ = "PRODUCTS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    sellPrice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    transaction_details = relationship("TransactionDetail", back_populates="product")

class Transaction(Base):
    __tablename__ = "TRANSACTIONS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    branch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("BRANCHES.id", ondelete="SET NULL"), nullable=True)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("CUSTOMERS.id", ondelete="SET NULL"), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    dateOfTransaction: Mapped[date] = mapped_column(Date, nullable=False)
    timeOfTransaction: Mapped[time] = mapped_column(Time, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    branch = relationship("Branch", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    details = relationship("TransactionDetail", back_populates="transaction", cascade="all, delete-orphan")

class TransactionDetail(Base):
    __tablename__ = "TRANSACTION_DETAILS"

    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("TRANSACTIONS.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("PRODUCTS.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    transaction = relationship("Transaction", back_populates="details")
    product = relationship("Product", back_populates="transaction_details")

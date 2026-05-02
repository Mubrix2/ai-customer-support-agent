# app/db/models.py
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Order(Base):
    """Represents a customer order in the system."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), unique=True, nullable=False, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(
        Enum("pending", "processing", "shipped", "delivered", "cancelled", name="order_status"),
        nullable=False,
        default="pending",
    )
    total_amount = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_delivery = Column(String(50), nullable=True)
    tracking_number = Column(String(50), nullable=True)


class Complaint(Base):
    """A complaint logged by the agent during a support conversation."""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    customer_name = Column(String(100), nullable=True)
    order_id = Column(String(20), nullable=True)
    complaint_text = Column(Text, nullable=False)
    category = Column(
        Enum("delivery", "product", "billing", "service", "other", name="complaint_category"),
        nullable=False,
        default="other",
    )
    status = Column(
        Enum("open", "in_review", "resolved", name="complaint_status"),
        nullable=False,
        default="open",
    )
    created_at = Column(DateTime, default=datetime.utcnow)


class Escalation(Base):
    """A conversation flagged for human agent review."""
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    conversation_summary = Column(Text, nullable=True)
    status = Column(
        Enum("pending", "assigned", "resolved", name="escalation_status"),
        nullable=False,
        default="pending",
    )
    created_at = Column(DateTime, default=datetime.utcnow)
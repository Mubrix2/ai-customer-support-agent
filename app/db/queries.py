# app/db/queries.py
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Complaint, Escalation, Order

logger = logging.getLogger(__name__)


# --- Order queries ---

def get_order_by_id(db: Session, order_id: str) -> dict | None:
    """
    Look up an order by its order ID.
    Returns a clean dict or None if not found.
    """
    order = db.query(Order).filter(Order.order_id == order_id.upper()).first()
    if not order:
        return None
    return {
        "order_id": order.order_id,
        "customer_name": order.customer_name,
        "product_name": order.product_name,
        "quantity": order.quantity,
        "status": order.status,
        "total_amount": order.total_amount,
        "estimated_delivery": order.estimated_delivery,
        "tracking_number": order.tracking_number,
        "created_at": order.created_at.strftime("%Y-%m-%d"),
    }


def get_orders_by_email(db: Session, email: str) -> list[dict]:
    """Look up all orders for a customer email address."""
    orders = db.query(Order).filter(Order.customer_email == email.lower()).all()
    return [
        {
            "order_id": o.order_id,
            "product_name": o.product_name,
            "status": o.status,
            "total_amount": o.total_amount,
            "created_at": o.created_at.strftime("%Y-%m-%d"),
        }
        for o in orders
    ]


# --- Complaint queries ---

def create_complaint(
    db: Session,
    session_id: str,
    complaint_text: str,
    category: str,
    customer_name: str | None = None,
    order_id: str | None = None,
) -> dict:
    """Log a new complaint from a support conversation."""
    complaint = Complaint(
        session_id=session_id,
        customer_name=customer_name,
        order_id=order_id,
        complaint_text=complaint_text,
        category=category,
        status="open",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    logger.info(f"Complaint logged: id={complaint.id} session={session_id}")
    return {
        "complaint_id": complaint.id,
        "status": complaint.status,
        "category": complaint.category,
        "created_at": complaint.created_at.strftime("%Y-%m-%d %H:%M"),
    }


# --- Escalation queries ---

def create_escalation(
    db: Session,
    session_id: str,
    reason: str,
    conversation_summary: str | None = None,
) -> dict:
    """Flag a conversation for human agent review."""
    escalation = Escalation(
        session_id=session_id,
        reason=reason,
        conversation_summary=conversation_summary,
        status="pending",
    )
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    logger.info(f"Escalation created: id={escalation.id} session={session_id}")
    return {
        "escalation_id": escalation.id,
        "status": escalation.status,
        "created_at": escalation.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def get_escalation_by_session(db: Session, session_id: str) -> dict | None:
    """Check if a session has already been escalated."""
    escalation = (
        db.query(Escalation)
        .filter(Escalation.session_id == session_id)
        .first()
    )
    if not escalation:
        return None
    return {
        "escalation_id": escalation.id,
        "status": escalation.status,
        "reason": escalation.reason,
    }
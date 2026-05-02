# app/core/tools.py
import logging
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.db import queries

logger = logging.getLogger(__name__)


@tool
def check_order_status(order_id: str) -> str:
    """
    Look up the status of a customer order by order ID.
    Use this when the customer provides an order ID like ORD-001, ORD-002, etc.

    Args:
        order_id: The order ID provided by the customer (e.g., ORD-001)

    Returns:
        Order details including status, product, and estimated delivery,
        or a message indicating the order was not found.
    """
    db = SessionLocal()
    try:
        order = queries.get_order_by_id(db, order_id.strip().upper())
        if not order:
            return (
                f"No order found with ID '{order_id}'. "
                "Please check the order ID and try again. "
                "Order IDs follow the format ORD-001."
            )
        status_messages = {
            "pending": "Your order has been received and is awaiting processing.",
            "processing": "Your order is currently being prepared for shipment.",
            "shipped": f"Your order is on its way! Tracking number: {order.get('tracking_number', 'N/A')}",
            "delivered": "Your order has been delivered.",
            "cancelled": "This order has been cancelled.",
        }
        status_msg = status_messages.get(order["status"], order["status"])
        result = (
            f"Order ID: {order['order_id']}\n"
            f"Product: {order['product_name']}\n"
            f"Quantity: {order['quantity']}\n"
            f"Amount: {order['total_amount']}\n"
            f"Status: {order['status'].upper()} — {status_msg}\n"
            f"Order Date: {order['created_at']}\n"
        )
        if order.get("estimated_delivery"):
            result += f"Estimated Delivery: {order['estimated_delivery']}\n"
        if order.get("tracking_number"):
            result += f"Tracking Number: {order['tracking_number']}\n"
        return result
    except Exception as e:
        logger.error(f"check_order_status failed: {e}")
        return "I was unable to retrieve order information at this time. Please try again."
    finally:
        db.close()


@tool
def get_orders_by_email(email: str) -> str:
    """
    Look up all orders associated with a customer email address.
    Use this when the customer provides their email and wants to see their order history.

    Args:
        email: The customer's email address

    Returns:
        A list of orders associated with the email, or a not found message.
    """
    db = SessionLocal()
    try:
        orders = queries.get_orders_by_email(db, email.strip().lower())
        if not orders:
            return (
                f"No orders found for email '{email}'. "
                "Please check the email address or contact support."
            )
        result = f"Found {len(orders)} order(s) for {email}:\n\n"
        for order in orders:
            result += (
                f"• {order['order_id']} — {order['product_name']} "
                f"({order['status'].upper()}) — {order['total_amount']} "
                f"— Ordered: {order['created_at']}\n"
            )
        return result
    except Exception as e:
        logger.error(f"get_orders_by_email failed: {e}")
        return "I was unable to retrieve order history at this time."
    finally:
        db.close()


@tool
def log_complaint(
    session_id: str,
    complaint_text: str,
    category: str,
    customer_name: str = "",
    order_id: str = "",
) -> str:
    """
    Log a customer complaint to the database.
    Use this when a customer expresses dissatisfaction or reports a problem.
    Always confirm with the customer before logging.

    Args:
        session_id: The current conversation session ID
        complaint_text: A clear description of the complaint
        category: One of: delivery, product, billing, service, other
        customer_name: Customer's name if known
        order_id: Related order ID if applicable

    Returns:
        Confirmation message with complaint reference number.
    """
    db = SessionLocal()
    try:
        valid_categories = ["delivery", "product", "billing", "service", "other"]
        if category not in valid_categories:
            category = "other"

        result = queries.create_complaint(
            db=db,
            session_id=session_id,
            complaint_text=complaint_text,
            category=category,
            customer_name=customer_name or None,
            order_id=order_id or None,
        )
        return (
            f"Your complaint has been logged successfully.\n"
            f"Reference Number: COMP-{result['complaint_id']:04d}\n"
            f"Category: {result['category'].title()}\n"
            f"Status: {result['status'].title()}\n"
            f"Logged at: {result['created_at']}\n"
            f"Our team will review this and follow up within 24-48 hours."
        )
    except Exception as e:
        logger.error(f"log_complaint failed: {e}")
        return "I was unable to log the complaint at this time. Please try again."
    finally:
        db.close()


@tool
def get_business_info(topic: str) -> str:
    """
    Get information about TechMart Nigeria's policies, hours, and contact details.
    Use this for questions about store hours, return policy, warranty, or contact info.

    Args:
        topic: The topic the customer is asking about (e.g., 'return policy', 'contact', 'hours')

    Returns:
        Relevant business information.
    """
    topic_lower = topic.lower()

    if any(word in topic_lower for word in ["hour", "open", "close", "time"]):
        return (
            "TechMart Nigeria Business Hours:\n"
            "Monday – Friday: 8:00 AM – 6:00 PM WAT\n"
            "Saturday: 9:00 AM – 4:00 PM WAT\n"
            "Sunday: Closed\n"
            "Public Holidays: Closed"
        )

    if any(word in topic_lower for word in ["return", "refund", "exchange"]):
        return (
            "TechMart Nigeria Return Policy:\n"
            "• Items can be returned within 7 days of delivery\n"
            "• Items must be unused and in original packaging\n"
            "• Refunds are processed within 5-7 business days\n"
            "• For defective items, contact support within 48 hours of delivery\n"
            "• Some items (e.g., software, opened headphones) are non-returnable"
        )

    if any(word in topic_lower for word in ["contact", "phone", "email", "reach", "support"]):
        return (
            "TechMart Nigeria Contact Information:\n"
            "Email: support@techmart.ng\n"
            "Phone: +234 800 TECH MART (0800-8324-6278)\n"
            "WhatsApp: +234 901 234 5678\n"
            "Live Chat: Available on our website Mon-Fri 8AM-6PM"
        )

    if any(word in topic_lower for word in ["warrant", "guarantee"]):
        return (
            "TechMart Nigeria Warranty Policy:\n"
            "• All electronics come with a minimum 1-year manufacturer warranty\n"
            "• Extended warranty available at purchase for an additional fee\n"
            "• Warranty covers manufacturing defects only\n"
            "• Physical damage and water damage are not covered"
        )

    if any(word in topic_lower for word in ["deliver", "shipping", "ship"]):
        return (
            "TechMart Nigeria Delivery Information:\n"
            "• Lagos: 1-2 business days\n"
            "• Other states: 3-5 business days\n"
            "• Free delivery on orders above ₦50,000\n"
            "• Standard delivery fee: ₦1,500 – ₦3,000 depending on location\n"
            "• Express delivery available for Lagos at ₦3,500"
        )

    return (
        "TechMart Nigeria — Your trusted electronics retailer.\n"
        "I can provide information about: business hours, return policy, "
        "warranty, delivery, and contact details.\n"
        "What would you like to know more about?"
    )


@tool
def escalate_to_human(
    session_id: str,
    reason: str,
    conversation_summary: str = "",
) -> str:
    """
    Escalate the current conversation to a human support agent.
    Use ONLY when: customer is extremely upset, issue requires account access,
    or customer explicitly requests a human agent.

    Args:
        session_id: The current conversation session ID
        reason: Why this conversation needs human attention
        conversation_summary: Brief summary of the conversation so far

    Returns:
        Confirmation that escalation was created.
    """
    db = SessionLocal()
    try:
        existing = queries.get_escalation_by_session(db, session_id)
        if existing:
            return (
                "This conversation has already been escalated to our team. "
                f"Escalation reference: ESC-{existing['escalation_id']:04d}. "
                "A human agent will contact you within 2 business hours."
            )

        result = queries.create_escalation(
            db=db,
            session_id=session_id,
            reason=reason,
            conversation_summary=conversation_summary,
        )
        return (
            f"I have escalated your case to our human support team.\n"
            f"Escalation Reference: ESC-{result['escalation_id']:04d}\n"
            f"A human agent will contact you within 2 business hours.\n"
            f"Our support hours are Monday-Friday, 8AM-6PM WAT."
        )
    except Exception as e:
        logger.error(f"escalate_to_human failed: {e}")
        return (
            "I was unable to process the escalation right now. "
            "Please call us directly at +234 800 TECH MART."
        )
    finally:
        db.close()


# Export all tools as a list for easy import
TOOLS = [
    check_order_status,
    get_orders_by_email,
    log_complaint,
    get_business_info,
    escalate_to_human,
]
# tests/test_tools.py
import pytest
from unittest.mock import patch, MagicMock
from app.core.tools import (
    check_order_status,
    get_orders_by_email,
    log_complaint,
    get_business_info,
    escalate_to_human,
    TOOLS,
)


def test_tools_list_has_five_tools():
    assert len(TOOLS) == 5


def test_get_business_info_hours():
    result = get_business_info.invoke({"topic": "business hours"})
    assert "Monday" in result
    assert "8:00 AM" in result


def test_get_business_info_returns():
    result = get_business_info.invoke({"topic": "return policy"})
    assert "7 days" in result
    assert "refund" in result.lower()


def test_get_business_info_contact():
    result = get_business_info.invoke({"topic": "contact information"})
    assert "support@techmart.ng" in result


def test_get_business_info_delivery():
    result = get_business_info.invoke({"topic": "delivery"})
    assert "Lagos" in result


@patch("app.core.tools.SessionLocal")
def test_check_order_status_not_found(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = check_order_status.invoke({"order_id": "ORD-999"})
    assert "No order found" in result


@patch("app.core.tools.SessionLocal")
@patch("app.core.tools.queries.get_order_by_id")
def test_check_order_status_found(mock_get_order, mock_session):
    mock_session.return_value = MagicMock()
    mock_get_order.return_value = {
        "order_id": "ORD-001",
        "customer_name": "Amina Bello",
        "product_name": "Wireless Headphones",
        "quantity": 1,
        "status": "delivered",
        "total_amount": "₦45,000",
        "estimated_delivery": "2026-04-20",
        "tracking_number": "TRK-881234",
        "created_at": "2026-04-15",
    }

    result = check_order_status.invoke({"order_id": "ORD-001"})
    assert "ORD-001" in result
    assert "DELIVERED" in result


@patch("app.core.tools.SessionLocal")
@patch("app.core.tools.queries.create_complaint")
def test_log_complaint_success(mock_create, mock_session):
    mock_session.return_value = MagicMock()
    mock_create.return_value = {
        "complaint_id": 1,
        "status": "open",
        "category": "delivery",
        "created_at": "2026-05-01 10:00",
    }

    result = log_complaint.invoke({
        "session_id": "test-session-123",
        "complaint_text": "My order has not arrived",
        "category": "delivery",
    })
    assert "COMP-0001" in result
    assert "logged successfully" in result
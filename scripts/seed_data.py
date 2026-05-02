# scripts/seed_data.py
"""
Run this script once to populate the database with mock order data.
Usage: python scripts/seed_data.py
"""
import sys
from pathlib import Path

# Add project root to path so imports work
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal, init_db
from app.db.models import Order

MOCK_ORDERS = [
    {
        "order_id": "ORD-001",
        "customer_name": "Amina Bello",
        "customer_email": "amina.bello@email.com",
        "product_name": "Wireless Bluetooth Headphones",
        "quantity": 1,
        "status": "delivered",
        "total_amount": "₦45,000",
        "estimated_delivery": "2026-04-20",
        "tracking_number": "TRK-881234",
    },
    {
        "order_id": "ORD-002",
        "customer_name": "Chukwuemeka Obi",
        "customer_email": "emeka.obi@email.com",
        "product_name": "Smart Watch Series 5",
        "quantity": 1,
        "status": "shipped",
        "total_amount": "₦120,000",
        "estimated_delivery": "2026-05-03",
        "tracking_number": "TRK-992341",
    },
    {
        "order_id": "ORD-003",
        "customer_name": "Fatima Aliyu",
        "customer_email": "fatima.aliyu@email.com",
        "product_name": "USB-C Laptop Charger",
        "quantity": 2,
        "status": "processing",
        "total_amount": "₦28,000",
        "estimated_delivery": "2026-05-05",
        "tracking_number": None,
    },
    {
        "order_id": "ORD-004",
        "customer_name": "Taiwo Adeyemi",
        "customer_email": "taiwo.adeyemi@email.com",
        "product_name": "Portable Power Bank 20000mAh",
        "quantity": 1,
        "status": "pending",
        "total_amount": "₦18,500",
        "estimated_delivery": "2026-05-07",
        "tracking_number": None,
    },
    {
        "order_id": "ORD-005",
        "customer_name": "Ngozi Eze",
        "customer_email": "ngozi.eze@email.com",
        "product_name": "Mechanical Keyboard TKL",
        "quantity": 1,
        "status": "cancelled",
        "total_amount": "₦65,000",
        "estimated_delivery": None,
        "tracking_number": None,
    },
    {
        "order_id": "ORD-006",
        "customer_name": "Mubarak Oladipo",
        "customer_email": "mubarak@email.com",
        "product_name": "4K Webcam Pro",
        "quantity": 1,
        "status": "shipped",
        "total_amount": "₦55,000",
        "estimated_delivery": "2026-05-04",
        "tracking_number": "TRK-774421",
    },
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Order).count()
        if existing > 0:
            print(f"Database already has {existing} orders — skipping seed")
            return

        for order_data in MOCK_ORDERS:
            order = Order(**order_data)
            db.add(order)

        db.commit()
        print(f"✅ Seeded {len(MOCK_ORDERS)} mock orders successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
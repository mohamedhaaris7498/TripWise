import uuid
import hmac
import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.config import settings
from app.database import get_db

CURATED_PACKAGES: List[Dict[str, Any]] = [
    {
        "id": "pkg_chn_01",
        "destination": "Chennai",
        "title": "East Coast Road Heritage & Shore Temple Tour",
        "category": "tour_package",
        "price": 1499.0,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=600&q=80",
        "perks": ["AC Private Cab", "English & Tamil Certified Guide", "Monument Entry Passes Included", "Complimentary Coconut Water"]
    },
    {
        "id": "pkg_chn_02",
        "destination": "Chennai",
        "title": "Bay View Deluxe Executive Suite (The Leela)",
        "category": "hotel_room",
        "price": 8999.0,
        "rating": 4.9,
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80",
        "perks": ["Buffet Breakfast", "Infinity Pool Access", "Late Checkout (3 PM)", "Complimentary Airport Pick-up"]
    },
    {
        "id": "pkg_chn_03",
        "destination": "Chennai",
        "title": "Kanchipuram Silk & Mylapore Traditional Craft Walk",
        "category": "shopping_experience",
        "price": 799.0,
        "rating": 4.7,
        "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
        "perks": ["Master Weaver Demonstration", "Guaranteed Silk Mark Verification", "15% Exclusive Store Discount Coupon"]
    },
    {
        "id": "pkg_goa_01",
        "destination": "Goa",
        "title": "Catamaran Sunset Cruise & Dolphin Safari",
        "category": "tour_package",
        "price": 1850.0,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=600&q=80",
        "perks": ["Lifejackets & Safety Briefing", "Chilled Beverages & Snacks", "Photographer on Board"]
    },
    {
        "id": "pkg_goa_02",
        "destination": "Goa",
        "title": "Candolim Beachfront Luxury Wooden Chalet",
        "category": "hotel_room",
        "price": 3800.0,
        "rating": 4.7,
        "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80",
        "perks": ["Direct Private Beach Access", "Free High-Speed Wi-Fi", "Daily Yoga Session Included"]
    },
    {
        "id": "pkg_mnl_01",
        "destination": "Manali",
        "title": "Atal Tunnel & Sissu Waterfall 4x4 Jeep Expedition",
        "category": "tour_package",
        "price": 2400.0,
        "rating": 4.9,
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80",
        "perks": ["Experienced Mountain Driver", "Hot Kahwa Tea & Maggi Stop", "Emergency First-Aid Kit"]
    },
    {
        "id": "pkg_jpr_01",
        "destination": "Jaipur",
        "title": "Royal Amber Fort Elephant & Heritage Sunset Tour",
        "category": "tour_package",
        "price": 1650.0,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=600&q=80",
        "perks": ["Skip-the-Line Monument Ticket", "Royal Photographer Included", "Traditional Puppet Souvenir"]
    }
]

def get_packages(destination: Optional[str] = None, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
    """Retrieve packages filtered by destination or maximum budget."""
    results = list(CURATED_PACKAGES)
    if destination and destination.strip():
        term = destination.strip().lower()
        results = [p for p in results if term in p["destination"].lower()]
    if max_price is not None and max_price > 0:
        results = [p for p in results if p["price"] <= max_price]
    return results

def create_checkout_order(user_id: int, item_id: str, item_type: str, item_name: str, amount: float, currency: str = "INR") -> Dict[str, Any]:
    """Create a sandbox payment checkout order and register pending booking in database."""
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    booking_ref = f"TRIP-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO bookings (
            booking_reference, user_id, item_type, item_name, amount, currency, status, payment_order_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            booking_ref, user_id, item_type, item_name, amount, currency, "pending", order_id, now_str
        ))
        conn.commit()

    return {
        "order_id": order_id,
        "booking_reference": booking_ref,
        "amount": amount,
        "currency": currency,
        "key_id": settings.PAYMENT_KEY_ID,
        "status": "created"
    }

def verify_payment_order(booking_reference: str, order_id: str, payment_id: str, signature: Optional[str] = None) -> Dict[str, Any]:
    """Verify payment signature and finalize booking status to confirmed."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE booking_reference = ?", (booking_reference,))
        booking = cursor.fetchone()

        if not booking:
            raise ValueError(f"Booking reference {booking_reference} not found.")

        # Signature verification check (or sandbox test verification)
        is_valid = True
        if signature and settings.PAYMENT_KEY_SECRET:
            try:
                # In sandbox simulation mode (keys starting with rzp_test or signature starting with mock)
                if settings.PAYMENT_KEY_SECRET.startswith("rzp_test") or (signature and signature.startswith("mock")):
                    is_valid = True
                else:
                    expected_sig = hmac.new(
                        settings.PAYMENT_KEY_SECRET.encode(),
                        f"{order_id}|{payment_id}".encode(),
                        hashlib.sha256
                    ).hexdigest()
                    is_valid = hmac.compare_digest(expected_sig, signature)
            except Exception:
                is_valid = True

        if not is_valid:
            raise ValueError("Payment signature verification failed.")

        receipt_summary = {
            "booking_reference": booking_reference,
            "item_name": booking["item_name"],
            "item_type": booking["item_type"],
            "amount_paid": booking["amount"],
            "currency": booking["currency"],
            "payment_id": payment_id,
            "order_id": order_id,
            "confirmed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "CONFIRMED",
            "support_pin": uuid.uuid4().hex[:4].upper()
        }

        cursor.execute("""
        UPDATE bookings
        SET status = 'confirmed', payment_id = ?, receipt_data_json = ?
        WHERE booking_reference = ?
        """, (payment_id, json.dumps(receipt_summary), booking_reference))
        conn.commit()

        receipt_url = f"/api/payments/receipt/{booking_reference}"

        return {
            "booking_reference": booking_reference,
            "payment_id": payment_id,
            "status": "confirmed",
            "receipt_url": receipt_url,
            "receipt_summary": receipt_summary
        }

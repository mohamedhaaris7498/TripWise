import json
from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import Optional
from app.schemas.payment import (
    PackageListResponse, CheckoutCreateRequest, CheckoutCreateResponse,
    PaymentVerifyRequest, PaymentVerifyResponse
)
from app.services.payment_service import get_packages, create_checkout_order, verify_payment_order
from app.routes.deps import get_optional_user
from app.database import get_db

router = APIRouter(tags=["Travel Packages & Payments"])

@router.get("/api/packages", response_model=PackageListResponse)
async def list_packages(
    destination: Optional[str] = Query(None, description="Destination filter (e.g., Chennai, Goa, Manali, Jaipur)"),
    max_price: Optional[float] = Query(None, ge=0.0, description="Maximum package budget")
):
    """
    Module F: Curated Travel Packages, Hotel Rooms & Local Shopping Experiences.
    Returns cost-effective and premium options with itemized perks.
    """
    packages = get_packages(destination=destination, max_price=max_price)
    return PackageListResponse(packages=packages, total=len(packages))

@router.post("/api/payments/create-checkout", response_model=CheckoutCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout(
    payload: CheckoutCreateRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Create a sandbox payment checkout order for rooms, local packages, or shopping items.
    Generates a unique booking reference and order ID, and registers the booking as 'pending' in the database.
    """
    if payload.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order amount must be greater than zero."
        )

    user_id = current_user["id"] if current_user else 1

    try:
        order_data = create_checkout_order(
            user_id=user_id,
            item_id=payload.item_id,
            item_type=payload.item_type,
            item_name=payload.item_name,
            amount=payload.amount,
            currency=payload.currency or "INR"
        )
        return CheckoutCreateResponse(**order_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize payment checkout order: {str(e)}"
        )

@router.post("/api/payments/verify", response_model=PaymentVerifyResponse)
async def verify_payment(payload: PaymentVerifyRequest):
    """
    Verify sandbox payment signature and finalize transaction.
    Updates booking status to 'confirmed' and issues a digital travel receipt.
    """
    try:
        result = verify_payment_order(
            booking_reference=payload.booking_reference,
            order_id=payload.order_id,
            payment_id=payload.payment_id,
            signature=payload.signature
        )
        return PaymentVerifyResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment verification failed: {str(e)}"
        )

@router.get("/api/payments/receipt/{booking_reference}")
async def get_booking_receipt(booking_reference: str):
    """Retrieve digital receipt and confirmation status for a verified booking."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE booking_reference = ?", (booking_reference,))
        booking = cursor.fetchone()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with reference '{booking_reference}' was not found."
        )

    receipt = {}
    if booking.get("receipt_data_json"):
        try:
            receipt = json.loads(booking["receipt_data_json"])
        except Exception:
            pass

    return {
        "booking_reference": booking["booking_reference"],
        "status": booking["status"],
        "item_name": booking["item_name"],
        "item_type": booking["item_type"],
        "amount": booking["amount"],
        "currency": booking["currency"],
        "payment_id": booking["payment_id"],
        "created_at": booking["created_at"],
        "receipt_summary": receipt
    }

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PackageItem(BaseModel):
    id: str
    destination: str
    title: str
    category: str  # 'hotel_room', 'tour_package', 'shopping_experience', 'transport_pass'
    price: float
    rating: float
    image_url: Optional[str] = None
    perks: List[str] = []

class PackageListResponse(BaseModel):
    packages: List[PackageItem]
    total: int

class CheckoutCreateRequest(BaseModel):
    item_id: str = Field(..., description="ID of room, package or item")
    item_type: str = Field(..., description="hotel, package, shopping, or activity")
    item_name: str = Field(..., description="Display title of item")
    amount: float = Field(..., gt=0.0, description="Amount to charge")
    currency: Optional[str] = Field("INR", description="Currency code")

class CheckoutCreateResponse(BaseModel):
    order_id: str
    booking_reference: str
    amount: float
    currency: str
    key_id: str
    status: str

class PaymentVerifyRequest(BaseModel):
    booking_reference: str
    order_id: str
    payment_id: str
    signature: Optional[str] = None

class PaymentVerifyResponse(BaseModel):
    booking_reference: str
    payment_id: str
    status: str
    receipt_url: str
    receipt_summary: Dict[str, Any]

from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    password: str

class AddCouponRequest(BaseModel):
    website: str
    coupon: str
    desc: str
    type: str
    expiryDate: str | None = None
    startDate: str | None = None

class RateCouponRequest(BaseModel):
    coupon_id: str
    rating_change: int
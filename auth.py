from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, description="Full name of user")
    email: str = Field(..., min_length=3, max_length=120, description="Email address or username")
    password: str = Field(..., min_length=6, max_length=100, description="Secure user password")
    age: int = Field(..., ge=1, le=120, description="Age in years to determine demographic recommendations")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    location: Optional[str] = Field(None, max_length=100, description="Home city/location")

class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=3, description="Email or username")
    password: str = Field(..., min_length=1, description="Account password")

class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    age: int
    location: Optional[str] = None
    age_bracket: str
    created_at: str

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserProfileResponse


from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ============================================================
# AUTH SCHEMAS
# Used for login and returning JWT tokens
# ============================================================

class LoginRequest(BaseModel):
    # What the user sends when logging in
    email:    str
    password: str

class TokenResponse(BaseModel):
    # What we send back after successful login
    access_token: str
    token_type:   str = "bearer"
    role:         str  # so frontend knows if admin or employee


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    # What is needed to create a new user
    full_name: str
    email:     str
    password:  str       # plain password (we hash it in the router)
    role_id:   int       # 1 = admin, 2 = employee


class UserResponse(BaseModel):
    # What we send back when returning user data
    id:         int
    full_name:  str
    email:      str
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy models


# ============================================================
# ASSET SCHEMAS
# ============================================================

class AssetCreate(BaseModel):
    # What is needed to create a new asset
    asset_code:     str
    asset_name:     str
    asset_category: str
    asset_status:   str = "available"


class AssetResponse(BaseModel):
    # What we send back when returning asset data
    id:             int
    asset_code:     str
    asset_name:     str
    asset_category: str
    asset_status:   str
    created_at:     datetime

    class Config:
        from_attributes = True
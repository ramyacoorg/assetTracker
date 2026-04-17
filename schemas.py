from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role_id: int

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class AssetCreate(BaseModel):
    asset_code: str
    asset_name: str
    asset_category: str
    asset_status: str = "available"
    purchase_date: Optional[str] = None

class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_category: Optional[str] = None
    asset_status: Optional[str] = None
    purchase_date: Optional[str] = None

class AssetResponse(BaseModel):
    id: int
    asset_code: str
    asset_name: str
    asset_category: str
    asset_status: str
    purchase_date: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    asset_id: int
    employee_id: int

class AssignmentResponse(BaseModel):
    id: int
    asset_id: int
    employee_id: int
    assigned_date: datetime
    status: str
    class Config:
        from_attributes = True

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Role(Base):
    __tablename__ = "roles"

    id        = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    permissions = relationship("RolePermission", back_populates="role")
    users       = relationship("User", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id              = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(100), unique=True, nullable=False)

    roles = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id            = Column(Integer, primary_key=True, index=True)
    role_id       = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    role       = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    full_name     = Column(String(100), nullable=False)
    email         = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id       = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active     = Column(Boolean, default=True)
    photo_url     = Column(String(500), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")


class Asset(Base):
    __tablename__ = "assets"

    id             = Column(Integer, primary_key=True, index=True)
    asset_code     = Column(String(50), unique=True, nullable=False)
    asset_name     = Column(String(150), nullable=False)
    asset_category = Column(String(100), nullable=False)
    asset_status   = Column(String(50), default="available")
    purchase_date  = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)


class AssetIssue(Base):
    __tablename__ = "asset_issues"

    id                = Column(Integer, primary_key=True, index=True)
    asset_id          = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_description = Column(Text, nullable=False)
    issue_status      = Column(String(50), default="open")
    photo_url         = Column(String(500), nullable=True)
    reported_at       = Column(DateTime, default=datetime.utcnow)
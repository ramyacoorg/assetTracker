from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# ============================================================
# ROLES TABLE
# Stores the role types: admin, employee
# Think of this as the "type of ID card" in a company
# ============================================================
class Role(Base):
    __tablename__ = "roles"

    id        = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    # One role can have many permissions (through role_permissions)
    permissions = relationship("RolePermission", back_populates="role")
    # One role can have many users
    users       = relationship("User", back_populates="role")


# ============================================================
# PERMISSIONS TABLE
# Stores every possible action: "delete:asset", "view:inventory"
# Think of these as "door names" in the company building
# ============================================================
class Permission(Base):
    __tablename__ = "permissions"

    id              = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(100), unique=True, nullable=False)

    # One permission can be linked to many roles
    roles = relationship("RolePermission", back_populates="permission")


# ============================================================
# ROLE_PERMISSIONS TABLE (Junction/Bridge Table)
# Links which role gets which permission
# Example: role_id=1 (admin) → permission_id=4 (delete:asset)
# ============================================================
class RolePermission(Base):
    __tablename__ = "role_permissions"

    id            = Column(Integer, primary_key=True, index=True)
    role_id       = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    # Relationships to navigate back to Role and Permission
    role       = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


# ============================================================
# USERS TABLE (UPDATED)
# Now uses role_id instead of plain role string
# Password will be stored as a hash (never plain text!)
# ============================================================
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    full_name     = Column(String(100), nullable=False)
    email         = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    # ⬆️ renamed from "password" to "password_hash"
    # we NEVER store plain passwords!

    role_id       = Column(Integer, ForeignKey("roles.id"), nullable=False)
    # ⬆️ changed from role String to role_id linking to roles table

    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    # Relationship to navigate to the Role object
    role = relationship("Role", back_populates="users")


# ============================================================
# ASSETS TABLE (same as before, just cleaner)
# ============================================================
class Asset(Base):
    __tablename__ = "assets"

    id           = Column(Integer, primary_key=True, index=True)
    asset_code   = Column(String(50), unique=True, nullable=False)
    asset_name   = Column(String(150), nullable=False)
    asset_category = Column(String(100), nullable=False)
    asset_status = Column(String(50), default="available")
    purchase_date = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
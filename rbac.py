



from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import SessionLocal
import models

# ============================================================
# CONFIGURATION
# SECRET_KEY is used to sign the JWT token
# Never share this in real projects! Put it in .env file
# ============================================================
SECRET_KEY = "your_super_secret_key_change_this"
ALGORITHM  = "HS256"

# This tells FastAPI: "tokens come from /api/auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================================
# GET DATABASE SESSION
# Helper that gives us a DB connection
# Used as Depends(get_db) in every router
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# GET CURRENT USER
# Reads the JWT token from the request
# Finds the user in DB and returns them
# ============================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


# ============================================================
# REQUIRE PRIVILEGE (THE VAULT GUARD)
# This is the RBAC checker!
#
# How to use it on any route:
#   Depends(RequirePrivilege("delete:asset"))
#
# What it does:
#   1. Gets the current logged-in user
#   2. Finds their role
#   3. Checks if their role has the required permission
#   4. YES → allow    NO → block with 403 Forbidden
# ============================================================
def RequirePrivilege(required_permission: str):
    def checker(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Get all permissions for this user's role
        role_permissions = db.query(models.RolePermission).filter(
            models.RolePermission.role_id == current_user.role_id
        ).all()

        # Build a list of permission names
        permission_names = []
        for rp in role_permissions:
            permission = db.query(models.Permission).filter(
                models.Permission.id == rp.permission_id
            ).first()
            if permission:
                permission_names.append(permission.permission_name)

        # Check if required permission exists
        if required_permission not in permission_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: '{required_permission}'"
            )

        return current_user

    return checker

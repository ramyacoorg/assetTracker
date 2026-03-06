from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from rbac import get_db, SECRET_KEY, ALGORITHM
import models
import schemas

router = APIRouter()

# ============================================================
# PASSWORD HASHING SETUP
# bcrypt safely hashes passwords
# We NEVER store plain passwords in the database!
# ============================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    # "mypassword123" → "$2b$12$randomhashstring..."
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Checks if entered password matches the stored hash
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, role_name: str) -> str:
    # Creates a JWT token that expires in 24 hours
    expire  = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "user_id": user_id,
        "role":    role_name,
        "exp":     expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ============================================================
# LOGIN ROUTE
# POST /api/auth/login
# User sends email + password → gets back JWT token
# ============================================================
@router.post("/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):

    # Step 1: Find user by email
    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    # Step 2: Check password
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Step 3: Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated"
        )

    # Step 4: Get role name
    role = db.query(models.Role).filter(
        models.Role.id == user.role_id
    ).first()

    # Step 5: Create and return JWT token
    token = create_access_token(user_id=user.id, role_name=role.role_name)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         role.role_name
    }


# ============================================================
# REGISTER ROUTE
# POST /api/auth/register
# Creates a new user with hashed password
# ============================================================
@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if email already exists
    existing = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password before saving!
    new_user = models.User(
        full_name     = user_data.full_name,
        email         = user_data.email,
        password_hash = hash_password(user_data.password),
        role_id       = user_data.role_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from rbac import get_db, SECRET_KEY, ALGORITHM
import models
import schemas

router = APIRouter()

def hash_password(plain_password: str) -> str:
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def create_access_token(user_id: int, role_name: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "user_id": user_id,
        "role":    role_name,
        "exp":     expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated"
        )

    role = db.query(models.Role).filter(
        models.Role.id == user.role_id
    ).first()

    token = create_access_token(user_id=user.id, role_name=role.role_name)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         role.role_name
    }

@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

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

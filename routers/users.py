# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models, bcrypt

router = APIRouter()

@router.get("/")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    users = db.query(models.User).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "is_active": u.is_active,
            "role_id": u.role_id,
            "photo_url": u.photo_url,
            "created_at": str(u.created_at),
        }
        for u in users
    ]

@router.post("/add")
def add_user(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.User).filter(models.User.email == payload["email"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = bcrypt.hashpw(payload["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    new_user = models.User(
        full_name=payload["full_name"],
        email=payload["email"],
        password_hash=hashed,
        role_id=payload.get("role_id", 2),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "role_id": new_user.role_id,
        "photo_url": new_user.photo_url,
        "created_at": str(new_user.created_at),
    }

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.patch("/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {
        "id": user.id,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }

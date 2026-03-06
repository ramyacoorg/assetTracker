from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, RequirePrivilege
import models
import schemas

router = APIRouter()


# ============================================================
# GET ALL USERS
# Only Admin with "view:users" permission
# ============================================================
@router.get("/", response_model=list[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("view:users"))
):
    return db.query(models.User).all()


# ============================================================
# GET USER BY ID
# Only Admin with "view:users" permission
# ============================================================
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("view:users"))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================
# DELETE USER
# Only Admin with "view:users" permission
# ============================================================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("view:users"))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
# routers/profile.py
import os, shutil, uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models

router = APIRouter()
RAILWAY_URL = "https://assettracker-production-e745.up.railway.app"
UPLOAD_DIR = "uploads/profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo = current_user.photo_url
    if photo and not photo.startswith("http"):
        photo = f"{RAILWAY_URL}/{photo}"
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "is_active": current_user.is_active,
        "photo_url": photo,
        "created_at": str(current_user.created_at),
    }

@router.post("/upload-photo")
async def upload_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ext = photo.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"{UPLOAD_DIR}/{filename}"

    with open(filepath, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    current_user.photo_url = filepath
    db.commit()
    db.refresh(current_user)

    full_url = f"{RAILWAY_URL}/{filepath}"
    return {
        "message": "Photo uploaded successfully",
        "photo_url": full_url,
    }

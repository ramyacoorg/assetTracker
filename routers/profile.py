from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models
import os
import uuid

router = APIRouter()
UPLOAD_DIR = "uploads"
RAILWAY_URL = "https://assettracker-production-e745.up.railway.app"

@router.post("/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only image files allowed")

    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}-profile.{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    photo_url = f"{RAILWAY_URL}/uploads/{filename}"
    current_user.photo_url = photo_url
    db.commit()

    return {
        "message":   "Profile photo uploaded successfully!",
        "photo_url": photo_url
    }


@router.get("/me")
def get_my_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role = db.query(models.Role).filter(
        models.Role.id == current_user.role_id
    ).first()

    return {
        "id":        current_user.id,
        "full_name": current_user.full_name,
        "email":     current_user.email,
        "role":      role.role_name if role else "unknown",
        "photo_url": current_user.photo_url,
        "is_active": current_user.is_active,
    }

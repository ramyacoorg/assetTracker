from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"

# ============================================================
# UPLOAD PROFILE PHOTO
# POST /api/profile/photo
# Employee sends a photo file → saved to uploads folder
# URL saved in database
# ============================================================
@router.post("/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check file type — only images allowed!
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed (jpg, png, webp)"
        )

    # Create unique filename so files don't overwrite each other
    # Example: abc123-profile.jpg
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}-profile.{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save file to uploads folder
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # Save URL to database
    photo_url = f"http://localhost:8000/uploads/{filename}"
    current_user.photo_url = photo_url
    db.commit()

    return {
        "message": "Profile photo uploaded successfully!",
        "photo_url": photo_url
    }


# ============================================================
# GET MY PROFILE
# GET /api/profile/me
# Returns current user info including photo
# ============================================================
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
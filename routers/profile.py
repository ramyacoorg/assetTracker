# routers/profile.py
import os, uuid, httpx
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models

router = APIRouter()

RAILWAY_URL    = "https://assettracker-production-e745.up.railway.app"
SUPABASE_URL   = "https://glvsjlmobgertxkbbjwl.supabase.co"
SUPABASE_KEY   = os.getenv("SUPABASE_KEY")          # add this env var in Railway
STORAGE_BUCKET = "profile-photos"                   # create this bucket in Supabase dashboard

@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo = current_user.photo_url
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
    if not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_KEY not set in environment")

    contents = await photo.read()
    ext = photo.filename.split(".")[-1].lower()
    filename = f"user_{current_user.id}_{uuid.uuid4().hex}.{ext}"

    # Upload to Supabase Storage
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": photo.content_type or "image/jpeg",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(upload_url, content=contents, headers=headers)
        if response.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Supabase upload failed: {response.text}")

    # Public URL
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"

    # Save to DB
    current_user.photo_url = public_url
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Photo uploaded successfully",
        "photo_url": public_url,
    }

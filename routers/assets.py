from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, RequirePrivilege
import models
import schemas

router = APIRouter()


# ============================================================
# CREATE ASSET
# Only admins with "add:asset" permission can do this
# ============================================================
@router.post("/", response_model=schemas.AssetResponse)
def create_asset(
    asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("add:asset"))
    # ⬆️ This checks: does the logged-in user have "add:asset" permission?
):
    db_asset = models.Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


# ============================================================
# GET ALL ASSETS
# Only users with "view:inventory" permission can see this
# (Admins only — employees use /my-gear instead)
# ============================================================
@router.get("/", response_model=list[schemas.AssetResponse])
def get_assets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("view:inventory"))
):
    return db.query(models.Asset).all()


# ============================================================
# GET ASSET BY ID
# Only users with "view:inventory" permission
# ============================================================
@router.get("/{asset_id}", response_model=schemas.AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("view:inventory"))
):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


# ============================================================
# UPDATE ASSET
# Only admins with "edit:asset" permission
# ============================================================
@router.put("/{asset_id}", response_model=schemas.AssetResponse)
def update_asset(
    asset_id: int,
    updated_asset: schemas.AssetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("edit:asset"))
):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for key, value in updated_asset.model_dump().items():
        setattr(asset, key, value)

    db.commit()
    db.refresh(asset)
    return asset


# ============================================================
# DELETE ASSET
# Only admins with "delete:asset" permission
# If an employee tries this → 403 Forbidden automatically!
# ============================================================
@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RequirePrivilege("delete:asset"))
    # ⬆️ THE VAULT GUARD 🔒
    # Even if someone manually sends a DELETE request,
    # they will get 403 Forbidden if they don't have this permission
):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted successfully"}

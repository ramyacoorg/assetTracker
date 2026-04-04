from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, RequirePrivilege, get_current_user
import models
import schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.AssetResponse])
def get_assets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Asset).all()

@router.get("/{asset_id}", response_model=schemas.AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/", response_model=schemas.AssetResponse)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(RequirePrivilege("add:asset"))):
    existing = db.query(models.Asset).filter(models.Asset.asset_code == asset.asset_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Asset code already exists")
    db_asset = models.Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.put("/{asset_id}", response_model=schemas.AssetResponse)
def update_asset(asset_id: int, updated: schemas.AssetUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(RequirePrivilege("edit:asset"))):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for key, value in updated.model_dump(exclude_none=True).items():
        setattr(asset, key, value)
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(RequirePrivilege("delete:asset"))):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted successfully"}

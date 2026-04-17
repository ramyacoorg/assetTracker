from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models
import io, base64

router = APIRouter()

def _make_qr_b64(value: str) -> str:
    """Generate a base64-encoded PNG QR code for `value`."""
    import qrcode
    img = qrcode.make(value)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


@router.get("/{asset_id}")
def get_qr(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Generate lazily if not yet stored
    if not asset.qr_value:
        asset.qr_value = f"ASSENTRA_{asset.asset_code}"
        asset.qr_code = _make_qr_b64(asset.qr_value)
        db.commit()
        db.refresh(asset)
    elif not asset.qr_code:
        asset.qr_code = _make_qr_b64(asset.qr_value)
        db.commit()
        db.refresh(asset)

    return {
        "asset_id": asset.id,
        "asset_code": asset.asset_code,
        "asset_name": asset.asset_name,
        "qr_value": asset.qr_value,
        "qr_code": asset.qr_code,
    }


@router.get("/scan/{qr_value}")
def scan_qr(
    qr_value: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Look up an asset by its QR value."""
    asset = db.query(models.Asset).filter(models.Asset.qr_value == qr_value).first()
    if not asset:
        raise HTTPException(status_code=404, detail="No asset found for this QR code")
    return {
        "asset_id": asset.id,
        "asset_code": asset.asset_code,
        "asset_name": asset.asset_name,
        "asset_category": asset.asset_category,
        "asset_status": asset.asset_status,
        "purchase_date": str(asset.purchase_date) if asset.purchase_date else None,
        "repair_count": asset.repair_count,
    }

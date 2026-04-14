# routers/issues.py
import os, shutil, uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models

router = APIRouter()
RAILWAY_URL = "https://assettracker-production-e745.up.railway.app"
UPLOAD_DIR = "uploads/issues"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def build_photo_url(photo_url: str | None) -> str | None:
    if not photo_url:
        return None
    if photo_url.startswith("http"):
        return photo_url
    return f"{RAILWAY_URL}/{photo_url}"

@router.post("/report")
async def report_issue(
    asset_id: int = Form(...),
    issue_description: str = Form(...),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo_path = None
    if photo and photo.filename:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = f"{UPLOAD_DIR}/{filename}"
        with open(filepath, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_path = filepath

    issue = models.AssetIssue(
        asset_id=asset_id,
        employee_id=current_user.id,
        issue_description=issue_description,
        issue_status="open",
        photo_url=photo_path,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    return {
        "id": issue.id,
        "asset_id": issue.asset_id,
        "employee_id": issue.employee_id,
        "issue_description": issue.issue_description,
        "issue_status": issue.issue_status,
        "reported_at": str(issue.reported_at),
        "photo_url": build_photo_url(issue.photo_url),
    }

@router.get("/all")
def get_all_issues(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    issues = db.query(models.AssetIssue).order_by(models.AssetIssue.reported_at.desc()).all()
    result = []
    for issue in issues:
        asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
        employee = db.query(models.User).filter(models.User.id == issue.employee_id).first()
        result.append({
            "id": issue.id,
            "asset_id": issue.asset_id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "employee_id": issue.employee_id,
            "employee_name": employee.full_name if employee else "Unknown",
            "issue_description": issue.issue_description,
            "issue_status": issue.issue_status,
            "reported_at": str(issue.reported_at),
            "photo_url": build_photo_url(issue.photo_url),
        })
    return result

@router.get("/my")
def get_my_issues(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    issues = (
        db.query(models.AssetIssue)
        .filter(models.AssetIssue.employee_id == current_user.id)
        .order_by(models.AssetIssue.reported_at.desc())
        .all()
    )
    result = []
    for issue in issues:
        asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
        result.append({
            "id": issue.id,
            "asset_id": issue.asset_id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "issue_description": issue.issue_description,
            "issue_status": issue.issue_status,
            "reported_at": str(issue.reported_at),
            "photo_url": build_photo_url(issue.photo_url),
        })
    return result

@router.patch("/{issue_id}/status")
def update_issue_status(
    issue_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    issue = db.query(models.AssetIssue).filter(models.AssetIssue.id == issue_id).first()
    if not issue:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.issue_status = payload["issue_status"]
    db.commit()
    return {"message": "Status updated", "issue_status": issue.issue_status}

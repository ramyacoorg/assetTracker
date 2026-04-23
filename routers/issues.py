# routers/issues.py
import os, uuid, httpx
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models

router = APIRouter()

RAILWAY_URL    = "https://assettracker-production-e745.up.railway.app"
SUPABASE_URL   = "https://glvsjlmobgertxkbbjwl.supabase.co"
SUPABASE_KEY   = os.getenv("SUPABASE_KEY")
STORAGE_BUCKET = "issue-photos"   # create this bucket in Supabase too

@router.post("/report")
async def report_issue(
    asset_id: int = Form(...),
    issue_description: str = Form(...),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo_url = None

    if photo and photo.filename:
        contents = await photo.read()
        ext = photo.filename.split(".")[-1].lower()
        filename = f"issue_{uuid.uuid4().hex}.{ext}"
        
        if SUPABASE_KEY:
            upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{filename}"
            headers = {
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": photo.content_type or "image/jpeg",
            }
            try:
                async with httpx.AsyncClient() as client:
                    res = await client.post(upload_url, content=contents, headers=headers)
                    if res.status_code in (200, 201):
                        photo_url = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{filename}"
            except Exception as e:
                print(f"Failed to upload photo: {e}")
        else:
            # Local fallback for storing issue photos
            os.makedirs("uploads/issues", exist_ok=True)
            local_path = os.path.join("uploads/issues", filename)
            with open(local_path, "wb") as f:
                f.write(contents)
            photo_url = f"http://localhost:8000/uploads/issues/{filename}"

    issue = models.AssetIssue(
        asset_id=asset_id,
        employee_id=current_user.id,
        issue_description=issue_description,
        issue_status="open",
        photo_url=photo_url,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
    
    # Simulated Email Notification
    print("\n" + "="*50)
    print("📧 [MOCK EMAIL SERVICE] -> Sent to: admins@assentra.local")
    print(f"Subject: New Issue Reported - Asset #{issue.asset_id}")
    print(f"Body: User #{issue.employee_id} reported an issue with asset '{asset.asset_name if asset else 'Unknown'}'.")
    print(f"Description: {issue.issue_description}")
    print("="*50 + "\n")

    return {
        "id": issue.id,
        "asset_id": issue.asset_id,
        "asset_name": asset.asset_name if asset else "Unknown",
        "employee_id": issue.employee_id,
        "issue_description": issue.issue_description,
        "issue_status": issue.issue_status,
        "reported_at": str(issue.reported_at),
        "photo_url": issue.photo_url,
    }

@router.get("/all")
def get_all_issues(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    issues = db.query(models.AssetIssue).order_by(models.AssetIssue.reported_at.desc()).all()
    result = []
    for issue in issues:
        asset    = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
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
            "photo_url": issue.photo_url,
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
            "photo_url": issue.photo_url,
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
        raise HTTPException(status_code=404, detail="Issue not found")
    new_status = payload.get("status") or payload.get("issue_status")
    if not new_status:
        raise HTTPException(status_code=422, detail="Missing 'status' field")
    issue.issue_status = new_status
    db.commit()
    return {"message": "Status updated", "issue_status": issue.issue_status}

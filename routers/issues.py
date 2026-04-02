from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models
import os
import uuid

router = APIRouter()
UPLOAD_DIR = "uploads"

# ============================================================
# REPORT AN ISSUE WITH OPTIONAL PHOTO
# POST /api/issues/report
# ============================================================
@router.post("/report")
async def report_issue(
    asset_id: int = Form(...),
    issue_description: str = Form(...),
    file: UploadFile = File(None),  # photo is optional
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    photo_url = None

    # If photo is attached, save it
    if file and file.filename:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
            raise HTTPException(status_code=400, detail="Only image files allowed")

        extension = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}-issue.{extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        photo_url = f"http://localhost:8000/uploads/{filename}"

    # Save issue to database
    new_issue = models.AssetIssue(
        asset_id          = asset_id,
        employee_id       = current_user.id,
        issue_description = issue_description,
        issue_status      = "open",
        photo_url         = photo_url
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return {
        "message":   "Issue reported successfully!",
        "issue_id":  new_issue.id,
        "photo_url": photo_url
    }


# ============================================================
# GET ALL ISSUES (Admin only)
# GET /api/issues/
# ============================================================
@router.get("/")
def get_all_issues(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    issues = db.query(models.AssetIssue).all()
    result = []
    for issue in issues:
        result.append({
            "id":                issue.id,
            "asset_id":          issue.asset_id,
            "employee_id":       issue.employee_id,
            "issue_description": issue.issue_description,
            "issue_status":      issue.issue_status,
            "photo_url":         issue.photo_url,
            "reported_at":       issue.reported_at,
        })
    return result
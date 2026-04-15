# routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from rbac import get_db, get_current_user
import models

router = APIRouter()
RAILWAY_URL = "https://assettracker-production-e745.up.railway.app"

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_assets   = db.query(func.count(models.Asset.id)).scalar() or 0
    assigned       = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "assigned").scalar() or 0
    available      = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "available").scalar() or 0
    under_repair   = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "under_repair").scalar() or 0
    retired        = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "retired").scalar() or 0
    total_users    = db.query(func.count(models.User.id)).scalar() or 0
    open_issues    = db.query(func.count(models.AssetIssue.id)).filter(models.AssetIssue.issue_status == "open").scalar() or 0
    resolved_issues = db.query(func.count(models.AssetIssue.id)).filter(models.AssetIssue.issue_status == "resolved").scalar() or 0

    category_counts = (
        db.query(models.Asset.asset_category, func.count(models.Asset.id))
        .group_by(models.Asset.asset_category)
        .all()
    )

    recent_issues_query = (
        db.query(models.AssetIssue)
        .order_by(models.AssetIssue.reported_at.desc())
        .limit(5)
        .all()
    )

    issues_data = []
    for issue in recent_issues_query:
        asset    = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
        employee = db.query(models.User).filter(models.User.id == issue.employee_id).first()
        photo = issue.photo_url
        if photo and not photo.startswith("http"):
            photo = f"{RAILWAY_URL}/{photo}"
        issues_data.append({
            "id": issue.id,
            "asset_id": issue.asset_id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "employee_name": employee.full_name if employee else "Unknown",
            "issue_description": issue.issue_description,
            "issue_status": issue.issue_status,
            "reported_at": str(issue.reported_at),
            "photo_url": photo,
        })

    return {
        "total_assets": total_assets,
        "assigned": assigned,
        "available": available,
        "under_repair": under_repair,
        "retired": retired,
        "total_users": total_users,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues,
        "category_counts": [{"category": c, "count": n} for c, n in category_counts],
        "recent_issues": issues_data,
    }


@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Real assigned assets count
    my_assignments = (
        db.query(models.AssetAssignment)
        .filter(
            models.AssetAssignment.employee_id == current_user.id,
            models.AssetAssignment.status == "active"
        )
        .all()
    )

    # Real assets details
    my_assets_data = []
    for a in my_assignments:
        asset = db.query(models.Asset).filter(models.Asset.id == a.asset_id).first()
        if asset:
            my_assets_data.append({
                "asset_id": asset.id,
                "asset_name": asset.asset_name,
                "asset_code": asset.asset_code,
                "asset_category": asset.asset_category,
                "asset_status": asset.asset_status,
                "assigned_date": str(a.assigned_date),
            })

    # Real issues
    my_issues = (
        db.query(models.AssetIssue)
        .filter(models.AssetIssue.employee_id == current_user.id)
        .order_by(models.AssetIssue.reported_at.desc())
        .all()
    )

    open_issues     = sum(1 for i in my_issues if i.issue_status == "open")
    resolved_issues = sum(1 for i in my_issues if i.issue_status == "resolved")
    total_issues    = len(my_issues)

    recent_issues_data = []
    for issue in my_issues[:5]:
        asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
        photo = issue.photo_url
        if photo and not photo.startswith("http"):
            photo = f"{RAILWAY_URL}/{photo}"
        recent_issues_data.append({
            "id": issue.id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "asset_code": asset.asset_code if asset else "",
            "issue_description": issue.issue_description,
            "issue_status": issue.issue_status,
            "reported_at": str(issue.reported_at),
            "photo_url": photo,
        })

    photo_url = current_user.photo_url
    if photo_url and not photo_url.startswith("http"):
        photo_url = f"{RAILWAY_URL}/{photo_url}"

    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "photo_url": photo_url,
        "my_assets_count": len(my_assignments),
        "open_tickets": open_issues,
        "resolved_tickets": resolved_issues,
        "total_tickets": total_issues,
        "my_assets": my_assets_data,
        "recent_issues": recent_issues_data,
    }

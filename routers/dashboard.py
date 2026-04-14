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
    total_assets = db.query(func.count(models.Asset.id)).scalar()
    assigned = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "assigned").scalar()
    available = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "available").scalar()
    under_repair = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "under_repair").scalar()
    retired = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "retired").scalar()
    total_users = db.query(func.count(models.User.id)).scalar()
    open_issues = db.query(func.count(models.AssetIssue.id)).filter(models.AssetIssue.issue_status == "open").scalar()
    resolved_issues = db.query(func.count(models.AssetIssue.id)).filter(models.AssetIssue.issue_status == "resolved").scalar()

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
        asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
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
    my_issues_query = (
        db.query(models.AssetIssue)
        .filter(models.AssetIssue.employee_id == current_user.id)
        .all()
    )

    open_issues = sum(1 for i in my_issues_query if i.issue_status == "open")
    total_issues = len(my_issues_query)

    return {
        "my_assets": 2,
        "open_tickets": open_issues,
        "total_tickets": total_issues,
        "full_name": current_user.full_name,
        "email": current_user.email,
    }

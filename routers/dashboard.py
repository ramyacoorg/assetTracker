# routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from rbac import get_db, get_current_user
import models

router = APIRouter()

@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_assets = db.query(func.count(models.Asset.id)).scalar()
    assigned = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "assigned").scalar()
    available = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "available").scalar()
    under_repair = db.query(func.count(models.Asset.id)).filter(models.Asset.asset_status == "under_repair").scalar()
    total_users = db.query(func.count(models.User.id)).scalar()
    open_issues = db.query(func.count(models.AssetIssue.id)).filter(models.AssetIssue.issue_status == "open").scalar()

    # Assets by category for bar chart
    category_counts = (
        db.query(models.Asset.asset_category, func.count(models.Asset.id))
        .group_by(models.Asset.asset_category)
        .all()
    )

    # Recent issues with asset and employee info
    recent_issues = (
        db.query(models.AssetIssue)
        .order_by(models.AssetIssue.reported_at.desc())
        .limit(5)
        .all()
    )

    RAILWAY_URL = "https://assettracker-production-e745.up.railway.app"

    issues_data = []
    for issue in recent_issues:
        asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
        employee = db.query(models.User).filter(models.User.id == issue.employee_id).first()
        issues_data.append({
            "id": issue.id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "employee_name": employee.full_name if employee else "Unknown",
            "issue_description": issue.issue_description,
            "issue_status": issue.issue_status,
            "reported_at": str(issue.reported_at),
            "photo_url": f"{RAILWAY_URL}{issue.photo_url}" if issue.photo_url and not issue.photo_url.startswith("http") else issue.photo_url,
        })

    return {
        "total_assets": total_assets,
        "assigned": assigned,
        "available": available,
        "under_repair": under_repair,
        "total_users": total_users,
        "open_issues": open_issues,
        "category_counts": [{"category": c, "count": n} for c, n in category_counts],
        "recent_issues": issues_data,
    }

@router.get("/employee")
def employee_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    RAILWAY_URL = "https://assettracker-production-e745.up.railway.app"

    my_assignments = (
        db.query(models.AssetAssignment)
        .filter(
            models.AssetAssignment.employee_id == current_user.id,
            models.AssetAssignment.status == "active"
        )
        .all()
    )

    my_issues = (
        db.query(models.AssetIssue)
        .filter(models.AssetIssue.employee_id == current_user.id)
        .order_by(models.AssetIssue.reported_at.desc())
        .limit(5)
        .all()
    )

    assets_data = []
    for assignment in my_assignments:
        asset = db.query(models.Asset).filter(models.Asset.id == assignment.asset_id).first()
        if asset:
            assets_data.append({
                "asset_name": asset.asset_name,
                "asset_code": asset.asset_code,
                "asset_category": asset.asset_category,
                "assigned_date": str(assignment.assigned_date),
            })

    issues_data = []
    for issue in my_issues:
        asset = db.query(models.Asset).filter(models.Asset.id == issue.asset_id).first()
        issues_data.append({
            "id": issue.id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "issue_description": issue.issue_description,
            "issue_status": issue.issue_status,
            "reported_at": str(issue.reported_at),
            "photo_url": f"{RAILWAY_URL}{issue.photo_url}" if issue.photo_url and not issue.photo_url.startswith("http") else issue.photo_url,
        })

    return {
        "my_assets_count": len(my_assignments),
        "my_open_issues": sum(1 for i in my_issues if i.issue_status == "open"),
        "my_assets": assets_data,
        "my_recent_issues": issues_data,
  }

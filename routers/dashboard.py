from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models

router = APIRouter()

# ============================================================
# ADMIN DASHBOARD STATS
# GET /api/dashboard/admin
# ============================================================
@router.get("/admin")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_assets = db.query(models.Asset).count()
    available = db.query(models.Asset).filter(models.Asset.asset_status == "available").count()
    assigned = db.query(models.Asset).filter(models.Asset.asset_status == "assigned").count()
    under_repair = db.query(models.Asset).filter(models.Asset.asset_status == "under_repair").count()
    retired = db.query(models.Asset).filter(models.Asset.asset_status == "retired").count()
    total_users = db.query(models.User).count()
    open_issues = db.query(models.AssetIssue).filter(models.AssetIssue.issue_status == "open").count()
    resolved_issues = db.query(models.AssetIssue).filter(models.AssetIssue.issue_status == "resolved").count()

    # Recent issues
    recent_issues = db.query(models.AssetIssue).order_by(
        models.AssetIssue.reported_at.desc()
    ).limit(5).all()

    return {
        "total_assets": total_assets,
        "available": available,
        "assigned": assigned,
        "under_repair": under_repair,
        "retired": retired,
        "total_users": total_users,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues,
        "recent_issues": [
            {
                "id": i.id,
                "asset_id": i.asset_id,
                "employee_id": i.employee_id,
                "issue_description": i.issue_description,
                "issue_status": i.issue_status,
                "photo_url": i.photo_url,
                "reported_at": str(i.reported_at),
            } for i in recent_issues
        ]
    }


# ============================================================
# EMPLOYEE DASHBOARD STATS
# GET /api/dashboard/employee
# ============================================================
@router.get("/employee")
def get_employee_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    my_issues = db.query(models.AssetIssue).filter(
        models.AssetIssue.employee_id == current_user.id
    ).count()

    open_issues = db.query(models.AssetIssue).filter(
        models.AssetIssue.employee_id == current_user.id,
        models.AssetIssue.issue_status == "open"
    ).count()

    return {
        "my_assets": 2,
        "open_tickets": open_issues,
        "total_tickets": my_issues,
        "full_name": current_user.full_name,
        "email": current_user.email,
    }

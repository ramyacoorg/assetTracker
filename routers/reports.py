# routers/reports.py
import csv, io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from rbac import get_db, get_current_user
import models

router = APIRouter()

@router.get("/summary")
def get_report_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Asset status breakdown
    status_counts = (
        db.query(models.Asset.asset_status, func.count(models.Asset.id))
        .group_by(models.Asset.asset_status)
        .all()
    )

    # Asset category breakdown
    category_counts = (
        db.query(models.Asset.asset_category, func.count(models.Asset.id))
        .group_by(models.Asset.asset_category)
        .all()
    )

    # Issue status breakdown
    issue_counts = (
        db.query(models.AssetIssue.issue_status, func.count(models.AssetIssue.id))
        .group_by(models.AssetIssue.issue_status)
        .all()
    )

    # Monthly assignments (last 6 months)
    monthly = (
        db.query(
            func.to_char(models.AssetAssignment.assigned_date, 'Mon YYYY').label("month"),
            func.count(models.AssetAssignment.id).label("count")
        )
        .group_by(func.to_char(models.AssetAssignment.assigned_date, 'Mon YYYY'))
        .order_by(func.min(models.AssetAssignment.assigned_date).desc())
        .limit(6)
        .all()
    )

    # All assets for table
    assets = db.query(models.Asset).all()
    assets_data = [
        {
            "asset_code": a.asset_code,
            "asset_name": a.asset_name,
            "asset_category": a.asset_category,
            "asset_status": a.asset_status,
            "purchase_date": str(a.purchase_date) if a.purchase_date else "",
        }
        for a in assets
    ]

    return {
        "status_counts": [{"status": s, "count": c} for s, c in status_counts],
        "category_counts": [{"category": cat, "count": c} for cat, c in category_counts],
        "issue_counts": [{"status": s, "count": c} for s, c in issue_counts],
        "monthly_assignments": [{"month": m, "count": c} for m, c in reversed(monthly)],
        "assets": assets_data,
        "total_assets": sum(c for _, c in status_counts),
        "total_issues": sum(c for _, c in issue_counts),
    }

@router.get("/export-csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    assets = db.query(models.Asset).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Asset Code", "Asset Name", "Category", "Status", "Purchase Date"])
    for a in assets:
        writer.writerow([
            a.asset_code,
            a.asset_name,
            a.asset_category,
            a.asset_status,
            str(a.purchase_date) if a.purchase_date else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=optiasset_report.csv"}
    )

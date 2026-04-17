# routers/hr.py  — Exit Checklist
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models

router = APIRouter()

@router.post("/exit-checklist/{employee_id}")
def generate_exit_checklist(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Auto-creates exit checklist entries for all active assignments of employee."""
    employee = db.query(models.User).filter(models.User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    active = (
        db.query(models.AssetAssignment)
        .filter(models.AssetAssignment.employee_id == employee_id, models.AssetAssignment.status == "active")
        .all()
    )
    created = []
    for a in active:
        # Avoid duplicates
        existing = db.query(models.ExitChecklist).filter(
            models.ExitChecklist.employee_id == employee_id,
            models.ExitChecklist.asset_id == a.asset_id,
        ).first()
        if not existing:
            entry = models.ExitChecklist(employee_id=employee_id, asset_id=a.asset_id, status="Pending")
            db.add(entry)
            created.append(a.asset_id)
    db.commit()
    return {"message": f"Checklist generated for {len(created)} asset(s)", "asset_ids": created}


@router.get("/exit-checklist")
def get_all_exit_checklists(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = db.query(models.ExitChecklist).all()
    result = []
    for item in items:
        employee = db.query(models.User).filter(models.User.id == item.employee_id).first()
        asset = db.query(models.Asset).filter(models.Asset.id == item.asset_id).first()
        result.append({
            "id": item.id,
            "employee_id": item.employee_id,
            "employee_name": employee.full_name if employee else "Unknown",
            "asset_id": item.asset_id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "asset_code": asset.asset_code if asset else "",
            "status": item.status,
        })
    return result


@router.patch("/exit-checklist/{item_id}/mark-returned")
def mark_returned(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.query(models.ExitChecklist).filter(models.ExitChecklist.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    item.status = "Returned"
    db.commit()
    return {"message": "Marked as returned", "status": "Returned"}

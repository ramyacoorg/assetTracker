# routers/assignments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rbac import get_db, get_current_user
import models
from datetime import date

router = APIRouter()

@router.get("/")
def get_all_assignments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    assignments = db.query(models.AssetAssignment).all()
    result = []
    for a in assignments:
        asset = db.query(models.Asset).filter(models.Asset.id == a.asset_id).first()
        employee = db.query(models.User).filter(models.User.id == a.employee_id).first()
        result.append({
            "id": a.id,
            "asset_id": a.asset_id,
            "asset_name": asset.asset_name if asset else "Unknown",
            "asset_code": asset.asset_code if asset else "",
            "employee_id": a.employee_id,
            "employee_name": employee.full_name if employee else "Unknown",
            "assigned_date": str(a.assigned_date),
            "return_date": str(a.return_date) if a.return_date else None,
            "status": a.status,
        })
    return result

@router.post("/assign")
def assign_asset(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check asset exists and is available
    asset = db.query(models.Asset).filter(models.Asset.id == payload["asset_id"]).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if asset.asset_status == "assigned":
        raise HTTPException(status_code=400, detail="Asset is already assigned")

    # Check employee exists
    employee = db.query(models.User).filter(models.User.id == payload["employee_id"]).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Create assignment
    new_assignment = models.AssetAssignment(
        asset_id=payload["asset_id"],
        employee_id=payload["employee_id"],
        assigned_date=date.today(),
        status="active",
    )
    db.add(new_assignment)

    # Update asset status
    asset.asset_status = "assigned"
    db.commit()
    db.refresh(new_assignment)

    return {
        "id": new_assignment.id,
        "asset_id": new_assignment.asset_id,
        "asset_name": asset.asset_name,
        "employee_id": new_assignment.employee_id,
        "employee_name": employee.full_name,
        "assigned_date": str(new_assignment.assigned_date),
        "status": new_assignment.status,
    }

@router.patch("/{assignment_id}/return")
def return_asset(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    assignment = db.query(models.AssetAssignment).filter(models.AssetAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.status = "returned"
    assignment.return_date = date.today()

    asset = db.query(models.Asset).filter(models.Asset.id == assignment.asset_id).first()
    if asset:
        asset.asset_status = "available"

    db.commit()
    return {"message": "Asset returned successfully"}

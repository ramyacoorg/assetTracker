# routers/audit.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from rbac import get_db, get_current_user
import models

router = APIRouter()

def log_action(db: Session, user_id: int, action: str, asset_id: Optional[int] = None, description: str = ""):
    """Helper — call this from any router to record an audit event."""
    entry = models.AuditLog(
        user_id=user_id,
        action=action,
        asset_id=asset_id,
        description=description,
    )
    db.add(entry)
    db.commit()

@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(200),
):
    query = db.query(models.AuditLog)
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    if action:
        query = query.filter(models.AuditLog.action == action)
    logs = query.order_by(models.AuditLog.timestamp.desc()).limit(limit).all()

    result = []
    for log in logs:
        user = db.query(models.User).filter(models.User.id == log.user_id).first()
        asset = db.query(models.Asset).filter(models.Asset.id == log.asset_id).first() if log.asset_id else None
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "user_name": user.full_name if user else "System",
            "action": log.action,
            "asset_id": log.asset_id,
            "asset_name": asset.asset_name if asset else None,
            "description": log.description,
            "timestamp": str(log.timestamp),
        })
    return result

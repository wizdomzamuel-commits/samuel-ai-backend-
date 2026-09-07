"""
CRUD endpoints for notifications.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.database import get_db
from app.schemas.notification import NotificationCreate, NotificationOut, NotificationUpdate
from app.services import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    return notification_service.create_notification(db, payload)


@router.get("", response_model=List[NotificationOut])
def list_notifications(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db),
):
    return notification_service.list_notifications(db, skip=skip, limit=limit, unread_only=unread_only)


@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification(notification_id: str, db: Session = Depends(get_db)):
    notification = notification_service.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.patch("/{notification_id}", response_model=NotificationOut)
def update_notification(notification_id: str, payload: NotificationUpdate, db: Session = Depends(get_db)):
    notification = notification_service.update_notification(db, notification_id, payload)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: str, db: Session = Depends(get_db)):
    deleted = notification_service.delete_notification(db, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")

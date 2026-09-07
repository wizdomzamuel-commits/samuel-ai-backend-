"""
Business logic / data-access layer for notifications.

Keeping this separate from the route handlers makes it easy to reuse the
same logic from the scheduler (for summaries) and from tests.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


def create_notification(db: Session, data: NotificationCreate) -> Notification:
    notification = Notification(
        title=data.title,
        body=data.body,
        source=data.source,
        priority=data.priority,
        app_name=data.app_name,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notification(db: Session, notification_id: str) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.id == notification_id).first()


def list_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
) -> List[Notification]:
    query = db.query(Notification)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def update_notification(
    db: Session, notification_id: str, data: NotificationUpdate
) -> Optional[Notification]:
    notification = get_notification(db, notification_id)
    if not notification:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)
    db.commit()
    db.refresh(notification)
    return notification


def delete_notification(db: Session, notification_id: str) -> bool:
    notification = get_notification(db, notification_id)
    if not notification:
        return False
    db.delete(notification)
    db.commit()
    return True


def get_notifications_since(db: Session, since: datetime) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(and_(Notification.created_at >= since))
        .order_by(Notification.created_at.asc())
        .all()
    )


def get_notifications_for_daily_summary(db: Session) -> List[Notification]:
    since = datetime.now(timezone.utc) - timedelta(days=1)
    return get_notifications_since(db, since)


def get_notifications_for_weekly_summary(db: Session) -> List[Notification]:
    since = datetime.now(timezone.utc) - timedelta(days=7)
    return get_notifications_since(db, since)

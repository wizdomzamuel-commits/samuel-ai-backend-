"""
Pydantic request/response schemas for notifications.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationPriority, NotificationSource


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    body: Optional[str] = None
    source: NotificationSource = NotificationSource.manual
    priority: NotificationPriority = NotificationPriority.normal
    app_name: Optional[str] = Field(default=None, max_length=120)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    body: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    is_read: Optional[bool] = None


class NotificationOut(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_read: bool
    created_at: datetime


class SummaryOut(BaseModel):
    period: str  # "daily" | "weekly"
    generated_at: datetime
    notification_count: int
    summary: str

"""
On-demand summary endpoints (daily / weekly).

These call the same logic the scheduler uses, so you can always trigger a
fresh summary manually via the API in addition to the automatic jobs.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.database import get_db
from app.schemas.notification import SummaryOut
from app.services import notification_service, openai_service

router = APIRouter(
    prefix="/summaries",
    tags=["summaries"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/daily", response_model=SummaryOut)
def get_daily_summary(db: Session = Depends(get_db)):
    notifications = notification_service.get_notifications_for_daily_summary(db)
    try:
        summary_text = openai_service.generate_summary(notifications, period="daily")
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return SummaryOut(
        period="daily",
        generated_at=datetime.now(timezone.utc),
        notification_count=len(notifications),
        summary=summary_text,
    )


@router.get("/weekly", response_model=SummaryOut)
def get_weekly_summary(db: Session = Depends(get_db)):
    notifications = notification_service.get_notifications_for_weekly_summary(db)
    try:
        summary_text = openai_service.generate_summary(notifications, period="weekly")
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return SummaryOut(
        period="weekly",
        generated_at=datetime.now(timezone.utc),
        notification_count=len(notifications),
        summary=summary_text,
    )

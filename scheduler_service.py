"""
Background scheduler that automatically generates daily and weekly
summaries and logs them (or, optionally, pushes them somewhere).

This runs in-process via APScheduler so no separate worker dyno is needed
on Railway. For heavier workloads you'd move this to a dedicated worker,
but it's the right tradeoff for a personal assistant.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.services import notification_service, openai_service

logger = logging.getLogger("samuel_ai.scheduler")
settings = get_settings()

scheduler = BackgroundScheduler(timezone=settings.TIMEZONE)


def _run_daily_summary_job() -> None:
    db = SessionLocal()
    try:
        notifications = notification_service.get_notifications_for_daily_summary(db)
        summary = openai_service.generate_summary(notifications, period="daily")
        logger.info("Daily summary generated (%d notifications):\n%s", len(notifications), summary)
        # TODO: send this somewhere (push notification, email, Slack, etc.)
    except Exception:
        logger.exception("Failed to generate daily summary")
    finally:
        db.close()


def _run_weekly_summary_job() -> None:
    db = SessionLocal()
    try:
        notifications = notification_service.get_notifications_for_weekly_summary(db)
        summary = openai_service.generate_summary(notifications, period="weekly")
        logger.info("Weekly summary generated (%d notifications):\n%s", len(notifications), summary)
        # TODO: send this somewhere (push notification, email, Slack, etc.)
    except Exception:
        logger.exception("Failed to generate weekly summary")
    finally:
        db.close()


def start_scheduler() -> None:
    if not settings.ENABLE_SCHEDULER:
        logger.info("Scheduler disabled via ENABLE_SCHEDULER=false")
        return

    scheduler.add_job(
        _run_daily_summary_job,
        trigger=CronTrigger(hour=settings.DAILY_SUMMARY_HOUR, minute=settings.DAILY_SUMMARY_MINUTE),
        id="daily_summary",
        replace_existing=True,
    )
    scheduler.add_job(
        _run_weekly_summary_job,
        trigger=CronTrigger(
            day_of_week=settings.WEEKLY_SUMMARY_DAY_OF_WEEK,
            hour=settings.WEEKLY_SUMMARY_HOUR,
        ),
        id="weekly_summary",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: daily @ %02d:%02d, weekly on %s @ %02d:00",
                settings.DAILY_SUMMARY_HOUR, settings.DAILY_SUMMARY_MINUTE,
                settings.WEEKLY_SUMMARY_DAY_OF_WEEK, settings.WEEKLY_SUMMARY_HOUR)


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)

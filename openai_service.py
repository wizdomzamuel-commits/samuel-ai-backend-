"""
OpenAI integration: turns a batch of notifications into a natural-language
summary for the daily/weekly digest.
"""

from typing import List

from openai import OpenAI

from app.core.config import get_settings
from app.models.notification import Notification

settings = get_settings()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to your environment or .env file."
            )
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def _format_notifications(notifications: List[Notification]) -> str:
    if not notifications:
        return "No notifications in this period."

    lines = []
    for n in notifications:
        ts = n.created_at.strftime("%Y-%m-%d %H:%M UTC")
        app = f" [{n.app_name}]" if n.app_name else ""
        body = f" — {n.body}" if n.body else ""
        lines.append(f"- ({ts}){app} {n.title}{body} (priority: {n.priority})")
    return "\n".join(lines)


def generate_summary(notifications: List[Notification], period: str) -> str:
    """
    Generate a concise natural-language summary of the given notifications.

    period: "daily" or "weekly" — used to tune the tone/length of the summary.
    """
    formatted = _format_notifications(notifications)

    system_prompt = (
        "You are Samuel AI, a personal assistant that writes short, useful "
        f"{period} briefings for your user based on their captured notifications. "
        "Group related items, call out anything high-priority or time-sensitive first, "
        "skip noise, and keep it skimmable. Use plain text with short bullet points. "
        "Do not invent information that isn't in the notifications provided."
    )

    user_prompt = (
        f"Here are the notifications from the last {'24 hours' if period == 'daily' else '7 days'}:\n\n"
        f"{formatted}\n\n"
        f"Write the {period} summary now."
    )

    client = get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()

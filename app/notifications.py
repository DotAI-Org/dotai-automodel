"""Google Chat webhook notification sender."""
import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_WEBHOOK_URL = None


def _get_webhook_url() -> str | None:
    """Return the cached webhook URL from environment."""
    global _WEBHOOK_URL
    if _WEBHOOK_URL is None:
        _WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL", "")
    return _WEBHOOK_URL or None


async def notify_gchat(title: str, detail: str) -> None:
    """Post an alert to Google Chat. No-ops if webhook URL is unset."""
    url = _get_webhook_url()
    if not url:
        return

    payload = {
        "text": f"*[Churn Tool Alert]*\n*Title:* {title}\n*Detail:* {detail}"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to send Google Chat notification: {e}")


def fire_and_forget(title: str, detail: str) -> None:
    """Schedule notify_gchat as a background task. Safe to call from anywhere."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(notify_gchat(title, detail))
    except RuntimeError:
        logger.debug("No running event loop; skipping notification")

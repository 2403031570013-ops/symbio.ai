import asyncio
from inspect import isawaitable
from uuid import uuid4

from app.models.notification import Notification
from app.services.email_service import send_email, EmailNotConfigured


def _run(coro):
    if isawaitable(coro):
        async def _awaitable_wrapper():
            return await coro

        return asyncio.run(_awaitable_wrapper())
    return asyncio.run(coro)


def create_notification(
    db,
    user_id: str,
    category: str,
    title: str,
    message: str,
    action_url: str | None = None,
    email: str | None = None,
) -> Notification:
    notification = Notification(
        id=str(uuid4()),
        user_id=user_id,
        category=category,
        title=title,
        message=message,
        action_url=action_url,
    )
    if email:
        try:
            send_email(email, title, message)
            notification.delivered_email = True
        except EmailNotConfigured:
            notification.delivered_email = False
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(notification.insert())
    else:
        _run(notification.insert())
    return notification

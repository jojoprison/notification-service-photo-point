import json
from celery import shared_task
from django.utils import timezone
from .models import Notification, NotificationAttempt


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_notification_task(self, notification_id: int):
    notif = Notification.objects.get(id=notification_id)
    order = notif.channels_order or ["telegram", "email", "sms"]
    for idx, channel in enumerate(order, start=1):
        NotificationAttempt.objects.create(
            notification=notif,
            channel=channel,
            provider="mock",
            attempt_no=idx,
            status="success",
        )
    notif.status = "sent"
    notif.save(update_fields=["status"])
    return {"notification_id": notification_id, "status": "sent"}

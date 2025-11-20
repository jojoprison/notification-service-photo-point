from django.db import models


class Notification(models.Model):
    STATUS_CHOICES = [
        ("queued", "queued"),
        ("processing", "processing"),
        ("sent", "sent"),
        ("delivered", "delivered"),
        ("failed", "failed"),
        ("partially_failed", "partially_failed"),
    ]
    user_id = models.BigIntegerField()
    template_id = models.CharField(max_length=128)
    payload_json = models.JSONField(default=dict)
    channels_order = models.JSONField(default=list)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="queued")
    idempotency_key = models.CharField(max_length=255, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "success"),
        ("failed", "failed"),
        ("retry_scheduled", "retry_scheduled"),
    ]
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="attempts")
    channel = models.CharField(max_length=32)
    provider = models.CharField(max_length=64)
    attempt_no = models.IntegerField(default=1)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    error_code = models.CharField(max_length=64, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    provider_message_id = models.CharField(max_length=128, null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

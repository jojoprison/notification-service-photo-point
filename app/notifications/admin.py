from django.contrib import admin
from .models import Notification, NotificationAttempt

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "template_id", "status", "created_at")
    search_fields = ("id", "user_id", "template_id", "idempotency_key")
    list_filter = ("status",)

@admin.register(NotificationAttempt)
class NotificationAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "notification", "channel", "provider", "status", "attempt_no", "created_at")
    search_fields = ("notification__id", "provider_message_id", "error_code")
    list_filter = ("channel", "provider", "status")

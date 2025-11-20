import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import SendNotificationSerializer
from .models import Notification
from .tasks import send_notification_task


class SendNotificationView(APIView):
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        channels = data.get("channelsOrder") or ["telegram", "email", "sms"]
        with transaction.atomic():
            notif = Notification.objects.create(
                user_id=data["userId"],
                template_id=data["templateId"],
                payload_json=data.get("payload", {}),
                channels_order=channels,
                idempotency_key=data.get("idempotencyKey"),
                status="queued",
            )
        send_notification_task.delay(notif.id)
        return Response({"notificationId": notif.id}, status=status.HTTP_202_ACCEPTED)


class NotificationStatusView(APIView):
    def get(self, request, pk: int):
        try:
            notif = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)
        attempts = [
            {
                "id": a.id,
                "channel": a.channel,
                "provider": a.provider,
                "attemptNo": a.attempt_no,
                "status": a.status,
                "errorCode": a.error_code,
                "errorMessage": a.error_message,
                "providerMessageId": a.provider_message_id,
                "nextRetryAt": a.next_retry_at,
                "createdAt": a.created_at,
            }
            for a in notif.attempts.all().order_by("created_at")
        ]
        return Response({
            "id": notif.id,
            "status": notif.status,
            "channelsOrder": notif.channels_order,
            "createdAt": notif.created_at,
            "attempts": attempts,
        })

from django.urls import path
from .views import SendNotificationView, NotificationStatusView

urlpatterns = [
    path("send", SendNotificationView.as_view(), name="send-notification"),
    path("<int:pk>", NotificationStatusView.as_view(), name="notification-status"),
]

from rest_framework import serializers


class SendNotificationSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    templateId = serializers.CharField()
    payload = serializers.DictField(child=serializers.JSONField(), default=dict)
    channelsOrder = serializers.ListField(child=serializers.CharField(), required=False)
    idempotencyKey = serializers.CharField(required=False, allow_null=True, allow_blank=True)

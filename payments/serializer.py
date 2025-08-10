from rest_framework.serializers import ModelSerializer
from .models import FileUpload, PaymentTransaction, ActivityLog

class FileUploadSerializer(ModelSerializer):
    class Meta:
        model = FileUpload
        fields = "__all__"

class PaymentTransactionSerializer(ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = "__all__"

class ActivityLogSerializer(ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
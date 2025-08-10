from django.contrib import admin
from .models import FileUpload, PaymentTransaction, ActivityLog


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("filename", "user", "status", "word_count", "upload_time")
    list_filter = ("status", "upload_time")
    search_fields = ("filename", "user__username", "user__email")
    ordering = ("-upload_time",)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user", "amount", "status", "timestamp")
    list_filter = ("status", "timestamp")
    search_fields = ("transaction_id", "user__username", "user__email")
    ordering = ("-timestamp",)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser



@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("user__username", "user__email", "action")
    ordering = ("-timestamp",)

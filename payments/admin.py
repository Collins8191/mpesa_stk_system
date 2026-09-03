from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "phone_number",
        "amount",
        "status",
        "result_code",
        "mpesa_receipt_number",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "phone_number",
        "checkout_request_id",
        "merchant_request_id",
        "mpesa_receipt_number",
    )

    ordering = (
        "-created_at",
    )
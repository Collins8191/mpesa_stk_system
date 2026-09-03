from django.db import models


class Payment(models.Model):
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    result_code = models.IntegerField(
        blank=True,
        null=True
    )

    result_description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.phone_number} - KES {self.amount}"
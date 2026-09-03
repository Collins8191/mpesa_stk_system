from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.core.paginator import Paginator




from .mpesa import lipa_na_mpesa
from .forms import PaymentForm
from .models import Payment


def test_mpesa(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            amount = form.cleaned_data["amount"]

            try:
                result = lipa_na_mpesa(phone, amount)

                # Safaricom/API error
                if not result.get("CheckoutRequestID"):
                    return render(request, "payments/payment.html", {
                        "form": form,
                        "error": "M-PESA payment request failed. Please try again."
                    })

                # Only create a payment after Safaricom accepts the STK request
                payment = Payment.objects.create(
                    phone_number=phone,
                    amount=amount,
                    merchant_request_id=result.get("MerchantRequestID"),
                    checkout_request_id=result.get("CheckoutRequestID"),
                    status="Pending"
                )

                return render(request, "payments/payment.html", {
                    "form": form,
                    "result": result,
                    "payment": payment
                })

            except Exception as e:
                print("M-PESA ERROR:", str(e))

                return render(request, "payments/payment.html", {
                    "form": form,
                    "error": "Unable to process M-PESA request. Please try again."
                })

    else:
        form = PaymentForm()

    return render(request, "payments/payment.html", {
        "form": form
    })


@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":

        import json

        data = request.body.decode("utf-8")

        print("===== M-PESA CALLBACK =====")
        print(data)

        try:
            callback_data = json.loads(data)

            stk_callback = callback_data["Body"]["stkCallback"]

            checkout_request_id = stk_callback.get(
                "CheckoutRequestID"
            )

            result_code = stk_callback.get(
                "ResultCode"
            )

            result_description = stk_callback.get(
                "ResultDesc"
            )

            payment = Payment.objects.filter(
                checkout_request_id=checkout_request_id
            ).first()

            if payment:

                payment.result_code = result_code
                payment.result_description = result_description

                if result_code == 0:
                    payment.status = "Success"

                    # Get transaction details
                    callback_items = stk_callback.get(
                        "CallbackMetadata", {}
                    ).get("Item", [])

                    for item in callback_items:

                        if item.get("Name") == "MpesaReceiptNumber":
                            payment.mpesa_receipt_number = item.get(
                                "Value"
                            )

                else:
                    payment.status = "Failed"

                payment.save()

                print("PAYMENT UPDATED:", payment.status)

                if payment.mpesa_receipt_number:
                    print(
                        "M-PESA RECEIPT:",
                        payment.mpesa_receipt_number
                    )

            else:
                print(
                    "PAYMENT NOT FOUND:",
                    checkout_request_id
                )

        except Exception as e:
            print("CALLBACK ERROR:", str(e))

        return JsonResponse({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })

    return JsonResponse({
        "error": "Only POST requests are allowed"
    }, status=405)


def payment_status(request, checkout_request_id):
    try:
        payment = Payment.objects.get(
            checkout_request_id=checkout_request_id
        )

        return JsonResponse({
            "status": payment.status,
            "result_code": payment.result_code,
            "result_description": payment.result_description,
            "receipt": payment.mpesa_receipt_number,
        })

    except Payment.DoesNotExist:
        return JsonResponse({
            "status": "Not Found"
        }, status=404)


@login_required
def payment_history(request):
    payments = Payment.objects.all().order_by("-created_at")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        payments = payments.filter(
            phone_number__icontains=search
        ) | payments.filter(
            mpesa_receipt_number__icontains=search
        )

    if status:
        payments = payments.filter(status=status)

    # Pagination
    paginator = Paginator(payments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_transactions = Payment.objects.count()

    successful_payments = Payment.objects.filter(
        status="Success"
    ).count()

    failed_payments = Payment.objects.filter(
        status="Failed"
    ).count()

    pending_payments = Payment.objects.filter(
        status="Pending"
    ).count()

    if total_transactions > 0:
        success_rate = (
            successful_payments / total_transactions
        ) * 100
    else:
        success_rate = 0

    total_revenue = Payment.objects.filter(
        status="Success"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    today = timezone.localdate()

    today_payments = Payment.objects.filter(
        created_at__date=today
    )

    today_transactions = today_payments.count()

    today_revenue = today_payments.filter(
        status="Success"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    return render(request, "payments/history.html", {
        "payments": page_obj,
        "page_obj": page_obj,
        "total_transactions": total_transactions,
        "successful_payments": successful_payments,
        "failed_payments": failed_payments,
        "pending_payments": pending_payments,
        "total_revenue": total_revenue,
        "success_rate": round(success_rate, 1),
        "today_transactions": today_transactions,
        "today_revenue": today_revenue,
        "search": search,
        "selected_status": status,
    })



@login_required
def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)

        return render(request, "payments/detail.html", {
            "payment": payment
        })

    except Payment.DoesNotExist:
        return render(request, "payments/detail.html", {
            "error": "Payment not found."
        }, status=404)
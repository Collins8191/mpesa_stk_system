import requests
import base64
from datetime import datetime
from django.conf import settings


def get_access_token():
    print("CONSUMER KEY EXISTS:", settings.MPESA_CONSUMER_KEY is not None)
    print("CONSUMER SECRET EXISTS:", settings.MPESA_CONSUMER_SECRET is not None)

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"

    response = requests.get(
        url,
        params={"grant_type": "client_credentials"},
        auth=(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET
        ),
        timeout=10
    )

    print("OAUTH STATUS:", response.status_code)
    print("OAUTH RESPONSE:", response.text)

    response.raise_for_status()

    return response.json()["access_token"]


def lipa_na_mpesa(phone_number, amount):
    access_token = get_access_token()

    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password_string = shortcode + passkey + timestamp

    password = base64.b64encode(
        password_string.encode()
    ).decode()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": "DjangoPayment",
        "TransactionDesc": "Django M-PESA Payment"
    }

    print("===== STK REQUEST =====")
    print("PHONE:", phone_number)
    print("AMOUNT:", amount)
    print("SHORTCODE:", shortcode)
    print("CALLBACK:", settings.MPESA_CALLBACK_URL)

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30
    )

    print("STK STATUS:", response.status_code)
    print("STK RESPONSE:", response.text)

    if response.status_code != 200:
        return {
            "status_code": response.status_code,
            "safaricom_response": response.text
        }

    return response.json()
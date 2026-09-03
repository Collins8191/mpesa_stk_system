from django import forms


class PaymentForm(forms.Form):

    phone_number = forms.CharField(
        max_length=15,
        label="M-PESA Phone Number",
        widget=forms.TextInput(attrs={
            "placeholder": "0712345678",
            "class": "form-control"
        })
    )

    amount = forms.DecimalField(
        min_value=1,
        max_value=150000,
        label="Amount (KES)",
        widget=forms.NumberInput(attrs={
            "placeholder": "Enter amount",
            "class": "form-control",
            "min": "1"
        })
    )

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()

        # Remove spaces and hyphens
        phone = phone.replace(" ", "").replace("-", "")

        # Convert +254XXXXXXXXX
        if phone.startswith("+254"):
            phone = phone[1:]

        # Convert 07XXXXXXXX
        elif phone.startswith("07"):
            phone = "254" + phone[1:]

        # Convert 01XXXXXXXX
        elif phone.startswith("01"):
            phone = "254" + phone[1:]

        # Validate final format
        if not phone.startswith("254"):
            raise forms.ValidationError(
                "Enter a valid Kenyan phone number."
            )

        if len(phone) != 12:
            raise forms.ValidationError(
                "Phone number must contain 12 digits."
            )

        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain digits only."
            )

        return phone
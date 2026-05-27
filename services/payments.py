import requests
import uuid
from django.conf import settings
from .models import WalletFunding

def initialize_payment(user, amount):
    reference = str(uuid.uuid4())

    WalletFunding.objects.create(
        user=user,
        amount=amount,
        reference=reference,
        status="pending"
    )

    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": user.email,
        "amount": int(amount * 100),  # kobo conversion
        "reference": reference,
        "callback_url": "https://your-domain.com/payment/callback/"
    }

    response = requests.post(url, json=data, headers=headers)

    return response.json()
    
    
def verify_payment(reference):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    return response.json()
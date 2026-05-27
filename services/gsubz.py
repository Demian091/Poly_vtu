from decimal import Decimal
import uuid
import requests
from django.conf import settings
from django.db import transaction

from .models import Transaction, Wallet



def get_plans(service):
      BASE_URL = settings.GSUBZ_BASE_URL
      
      url = f"{BASE_URL}/plans"
  
      headers = {
          "Authorization": f"Bearer {settings.GSUBZ_API_KEY}"
      }
  
      params = {
          "service": service
      }
  
      try:
          response = requests.get(url, headers=headers, params=params)
          response.raise_for_status()  # catches 4xx/5xx errors
  
          data = response.json()
  
          if not data or "plans" not in data:
              return []
  
          return data["plans"]
  
      except Exception as e:
          print("ERROR fetching plans:", e)
          return []
          

# def get_services():
#     url = f"{settings.GSUBZ_BASE_URL}/plans/"

#     headers = {
#         "Authorization": f"Bearer {settings.GSUBZ_API_KEY}"
#     }

#     response = requests.get(url, headers=headers)

#     data = response.json()

#     return data
    

class VTUService:

    @staticmethod
    def buy_data(user, service, plan, phone):

        # lock wallet for safe deduction
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=user)

            plans = get_plans(service)

            selected = next(
                (p for p in plans if p["value"] == plan),
                None
            )

            if not selected:
                return {"error": "Invalid plan"}

            api_price = Decimal(str(selected["price"]))
            profit = Decimal("30")
            user_price = api_price + profit

            if wallet.balance < user_price:
                return {"error": "Insufficient balance"}

            # create pending transaction FIRST
            tx = Transaction.objects.create(
                user=user,
                service=service,
                plan=plan,
                phone=phone,
                amount=user_price,
                status="pending",
                transaction_type="debit",
                transaction_id=str(uuid.uuid4())
            )

            payload = {
                "serviceID": service,
                "plan": plan,
                "phone": phone,
                "api": settings.GSUBZ_API_KEY,
                "amount": str(api_price),
                "requestID": tx.transaction_id
            }

            try:
                response = requests.post(
                    f"{settings.GSUBZ_BASE_URL}/pay/",
                    headers={
                        "Authorization": f"Bearer {settings.GSUBZ_API_KEY}"
                    },
                    data=payload,
                    timeout=30
                )

                data = response.json()

                if data.get("code") == 200:

                    # deduct wallet ONLY on success
                    wallet.balance -= user_price
                    wallet.save()

                    tx.status = "success"
                    tx.transaction_id = data.get("transactionID") or tx.transaction_id
                    tx.save()

                    return {
                        "code": 200,
                        "transaction_id": tx.id,
                        "message": "success"
                    }

                else:
                    tx.status = "failed"
                    tx.save()

                    return {
                        "code": 400,
                        "error": data.get("message", "Transaction failed"),
                        "transaction_id": tx.id
                    }

            except Exception as e:
                tx.status = "failed"
                tx.save()

                return {
                    "code": 500,
                    "error": str(e),
                    "transaction_id": tx.id
                }
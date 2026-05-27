from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from .forms import RegisterForm
import requests
from decimal import Decimal
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .gsubz import get_plans, VTUService
import uuid
import json
from .models import *

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def buy_data_view(request):
    service = request.data["service"]
    plan = request.data["plan"]
    phone = request.data["phone"]

    result = VTUService.buy_data(
        user=request.user,
        service=service,
        plan=plan,
        phone=phone
    )

    return Response(result)


@csrf_exempt
def paystack_webhook(request):
    payload = json.loads(request.body)

    print("PAYSTACK PAYLOAD:", payload)

    if payload["event"] == "charge.success":

        reference = payload["data"]["reference"]

        amount = Decimal(payload["data"]["amount"]) / Decimal("100")

        print("REFERENCE:", reference)
        print("AMOUNT:", amount)

        try:
            funding = WalletFunding.objects.get(reference=reference)

            print("FOUND FUNDING:", funding)

            if funding.status != "success":

                funding.status = "success"
                funding.save()

                wallet = Wallet.objects.get(user=funding.user)

                print("OLD BALANCE:", wallet.balance)

                wallet.balance += amount
                wallet.save()

                print("NEW BALANCE:", wallet.balance)

        except Exception as e:
            print("WEBHOOK ERROR:", e)

    return JsonResponse({"status": "ok"})
    
    
@login_required
def dashboard(request):
    wallet, created = Wallet.objects.get_or_create(
        user=request.user,
        defaults={"balance": 0}
    )

    transactions = wallet.user.transaction_set.all().order_by("-id")[:10]

    fundings = WalletFunding.objects.filter(
        user=request.user,
        status="success"
      ).order_by("-id")[:10]
      
    return render(request, "services/dashboard.html", {
        "wallet": wallet,
        "transactions": transactions,
        "fundings": fundings
    })
    

    
@api_view(["GET"])
def get_plans_view(request):
    service = request.GET.get("service")

    if not service:
        return Response({"error": "Service is required"}, status=400)

    plans = get_plans(service)
    
    for plan in plans:
      api_price = Decimal(plan["price"])
  
      profit = Decimal("30")
  
      user_price = api_price + profit
  
      plan["api_price"] = str(api_price)
      plan["user_price"] = str(user_price)

    return Response(plans)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    amount = int(request.data["amount"]) * 100
    email = request.user.email

    reference = str(uuid.uuid4())

    payload = {
        "email": email,
        "amount": amount,
        "reference": reference,
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=payload,
        headers=headers
    )

    data = response.json()

    WalletFunding.objects.create(
        user=request.user,
        reference=reference,
        amount=amount / 100,
        status="pending"
    )

    return Response({
        "authorization_url": data["data"]["authorization_url"]
    })


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.phone = form.cleaned_data["phone"]
            user.save()
            Wallet.objects.create(user=user, balance=0)
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "services/register.html", {"form": form})
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "services/login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "services/login.html")
    
def logout_view(request):
    logout(request)
    return redirect("login")


def transaction_receipt(request, tx_id):
    error = request.GET.get("error")

    if error:
        return render(request, "services/receipt.html", {
            "error": error
        })

    transaction = get_object_or_404(Transaction, id=tx_id, user=request.user)

    return render(request, "services/receipt.html", {
        "tx": transaction
    })


# @api_view(["GET"])
# def get_services_view(request):

#     services = [
#         {"id": "mtn_sme", "name": "MTN SME"},
#         {"id": "mtn_cg_lite", "name": "MTN SME 2.0"},
#         {"id": "mtn_awoof", "name": "MTN Awoof"},
#         {"id": "mtn_gifting", "name": "MTN Gifting"},
#         {"id": "mtn_datashare", "name": "MTN Data Share"},
#         {"id": "mtn_coupon", "name": "MTN Coupon"},
#         {"id": "mtncg", "name": "MTN Corporate Gifting"},
#         {"id": "airtel_cg", "name": "Airtel CG"},
#         {"id": "airtel_gifting", "name": "Airtel Gifting"},
#         {"id": "airtel_sme", "name": "Airtel SME"},
#         {"id": "glo_data", "name": "Glo Corporate"},
#         {"id": "glo_sme", "name": "Glo SME"},
#         {"id": "etisalat_data", "name": "9mobile"}
#     ]

#     active_services = []

#     for service in services:

#         plans = get_plans(service["id"])

#         if plans:
#             active_services.append(service)

#     return Response(active_services)


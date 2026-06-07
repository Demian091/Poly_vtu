from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Sum
from decimal import Decimal
import uuid
import requests
from django.conf import settings

from services.models import Wallet, Transaction, WalletFunding, APIKey
from .serializers import (
    UserSerializer, UserRegisterSerializer, WalletSerializer,
    TransactionSerializer, WalletFundingSerializer, APIKeySerializer,
    DataPlanSerializer, BuyDataRequestSerializer, FundWalletRequestSerializer,
    ChangePasswordSerializer, LoginSerializer
)
from services.gsubz import get_plans, VTUService

User = get_user_model()


# ============================================================
# AUTHENTICATION
# ============================================================

class RegisterView(APIView):
    """POST /api/auth/register/ - Register new user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create wallet and API key
            Wallet.objects.create(user=user, balance=Decimal('0.00'))
            APIKey.objects.create(user=user)
            return Response({
                'success': True,
                'message': 'Account created successfully.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """POST /api/auth/login/ - Login and get token"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)

        if not user:
            return Response({
                'success': False,
                'message': 'Invalid username or password.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create API key for token
        api_key, _ = APIKey.objects.get_or_create(user=user)

        return Response({
            'success': True,
            'message': 'Login successful.',
            'token': api_key.key,
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """POST /api/auth/logout/ - Logout user"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Optionally invalidate API key
        return Response({
            'success': True,
            'message': 'Logout successful.'
        })


# ============================================================
# USER PROFILE
# ============================================================

class ProfileView(APIView):
    """GET /api/profile/ - Get user profile"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        wallet = Wallet.objects.get(user=request.user)
        return Response({
            'success': True,
            'user': serializer.data,
            'wallet': WalletSerializer(wallet).data
        })

    def put(self, request):
        """Update profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Profile updated successfully.',
                'user': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """POST /api/profile/change-password/ - Change password"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'success': False,
                'message': 'Current password is incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({
            'success': True,
            'message': 'Password changed successfully.'
        })


# ============================================================
# WALLET
# ============================================================

class WalletBalanceView(APIView):
    """GET /api/wallet/balance/ - Get wallet balance"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(
            user=request.user,
            defaults={'balance': Decimal('0.00')}
        )
        return Response({
            'success': True,
            'balance': str(wallet.balance),
            'balance_formatted': f'₦{wallet.balance:,.2f}'
        })


class FundWalletView(APIView):
    """POST /api/wallet/fund/ - Initialize wallet funding"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FundWalletRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data['amount']
        email = request.user.email or f'{request.user.username}@polyvtu.com'
        reference = str(uuid.uuid4())

        payload = {
            'email': email,
            'amount': amount * 100,  # Paystack uses kobo
            'reference': reference,
        }

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                'https://api.paystack.co/transaction/initialize',
                json=payload,
                headers=headers,
                timeout=30
            )
            data = response.json()

            if not data.get('status'):
                return Response({
                    'success': False,
                    'message': data.get('message', 'Payment initialization failed.')
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create pending funding record
            WalletFunding.objects.create(
                user=request.user,
                reference=reference,
                amount=Decimal(str(amount)),
                status='pending'
            )

            return Response({
                'success': True,
                'message': 'Payment initialized.',
                'authorization_url': data['data']['authorization_url'],
                'reference': reference
            })

        except requests.RequestException:
            return Response({
                'success': False,
                'message': 'Payment service unavailable. Please try again.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ============================================================
# DATA PLANS
# ============================================================

class DataPlansView(APIView):
    """GET /api/data/plans/?service=mtn_sme - Get data plans"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        service = request.query_params.get('service')
        if not service:
            return Response({
                'success': False,
                'message': 'Service parameter is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            plans = get_plans(service)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to fetch plans: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Add pricing
        processed_plans = []
        for plan in plans:
            api_price = Decimal(str(plan.get('price', 0)))
            profit = Decimal('30')
            user_price = api_price + profit

            processed_plans.append({
                'plan_id': plan.get('plan_id', plan.get('id', '')),
                'name': plan.get('name', ''),
                'price': str(plan.get('price', 0)),
                'validity': plan.get('validity', ''),
                'api_price': str(api_price),
                'user_price': str(user_price),
                'size': plan.get('size', ''),
            })

        return Response({
            'success': True,
            'service': service,
            'plans': processed_plans
        })


# ============================================================
# BUY DATA
# ============================================================

class BuyDataView(APIView):
    """POST /api/data/buy/ - Purchase data"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BuyDataRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        service = serializer.validated_data['service']
        plan = serializer.validated_data['plan']
        phone = serializer.validated_data['phone']

        try:
            result = VTUService.buy_data(
                user=request.user,
                service=service,
                plan=plan,
                phone=phone
            )

            if result.get('status') == 'success':
                return Response({
                    'success': True,
                    'message': 'Data purchase successful.',
                    'transaction': result
                })
            else:
                return Response({
                    'success': False,
                    'message': result.get('message', 'Purchase failed.'),
                    'transaction': result
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Purchase error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# TRANSACTIONS
# ============================================================

class TransactionListView(APIView):
    """GET /api/transactions/ - List user transactions"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tx_type = request.query_params.get('type', '')
        status_filter = request.query_params.get('status', '')
        limit = int(request.query_params.get('limit', 50))

        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

        if tx_type:
            transactions = transactions.filter(transaction_type=tx_type)
        if status_filter:
            transactions = transactions.filter(status=status_filter)

        transactions = transactions[:limit]
        serializer = TransactionSerializer(transactions, many=True)

        # Summary stats
        total_spent = Transaction.objects.filter(
            user=request.user,
            status='success',
            transaction_type='debit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return Response({
            'success': True,
            'count': len(serializer.data),
            'total_spent': str(total_spent),
            'transactions': serializer.data
        })


class TransactionDetailView(APIView):
    """GET /api/transactions/<id>/ - Get transaction details"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk, user=request.user)
            serializer = TransactionSerializer(transaction)
            return Response({
                'success': True,
                'transaction': serializer.data
            })
        except Transaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found.'
            }, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# FUNDING HISTORY
# ============================================================

class FundingHistoryView(APIView):
    """GET /api/wallet/fundings/ - List wallet fundings"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        status_filter = request.query_params.get('status', '')
        limit = int(request.query_params.get('limit', 50))

        fundings = WalletFunding.objects.filter(user=request.user).order_by('-created_at')

        if status_filter:
            fundings = fundings.filter(status=status_filter)

        fundings = fundings[:limit]
        serializer = WalletFundingSerializer(fundings, many=True)

        # Summary stats
        total_funded = WalletFunding.objects.filter(
            user=request.user,
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return Response({
            'success': True,
            'count': len(serializer.data),
            'total_funded': str(total_funded),
            'fundings': serializer.data
        })


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

class DashboardView(APIView):
    """GET /api/dashboard/ - Get dashboard summary"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(
            user=request.user,
            defaults={'balance': Decimal('0.00')}
        )

        recent_transactions = Transaction.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        recent_fundings = WalletFunding.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        total_spent = Transaction.objects.filter(
            user=request.user,
            status='success',
            transaction_type='debit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total_funded = WalletFunding.objects.filter(
            user=request.user,
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        return Response({
            'success': True,
            'wallet': {
                'balance': str(wallet.balance),
                'balance_formatted': f'₦{wallet.balance:,.2f}'
            },
            'stats': {
                'total_spent': str(total_spent),
                'total_funded': str(total_funded),
                'transaction_count': Transaction.objects.filter(user=request.user).count(),
                'funding_count': WalletFunding.objects.filter(user=request.user).count()
            },
            'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
            'recent_fundings': WalletFundingSerializer(recent_fundings, many=True).data
        })

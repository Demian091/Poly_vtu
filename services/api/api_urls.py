from django.urls import path
from .api_views import (
    # Auth
    RegisterView, LoginView, LogoutView,
    # Profile
    ProfileView, ChangePasswordView,
    # Wallet
    WalletBalanceView, FundWalletView, FundingHistoryView,
    # Data
    DataPlansView, BuyDataView,
    # Transactions
    TransactionListView, TransactionDetailView,
    # Dashboard
    DashboardView,
)

urlpatterns = [
    # ==================== AUTH ====================
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),

    # ==================== PROFILE ====================
    path('profile/', ProfileView.as_view(), name='api_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='api_change_password'),

    # ==================== DASHBOARD ====================
    path('dashboard/', DashboardView.as_view(), name='api_dashboard'),

    # ==================== WALLET ====================
    path('wallet/balance/', WalletBalanceView.as_view(), name='api_wallet_balance'),
    path('wallet/fund/', FundWalletView.as_view(), name='api_fund_wallet'),
    path('wallet/fundings/', FundingHistoryView.as_view(), name='api_funding_history'),

    # ==================== DATA ====================
    path('data/plans/', DataPlansView.as_view(), name='api_data_plans'),
    path('data/buy/', BuyDataView.as_view(), name='api_buy_data'),

    # ==================== TRANSACTIONS ====================
    path('transactions/', TransactionListView.as_view(), name='api_transactions'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='api_transaction_detail'),
]

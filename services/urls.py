from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ==================== WEB VIEWS ====================
    path('', dashboard, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('transactions/', transaction_history, name='transactions'),
    path('settings/', settings_view, name='settings'),
    path('funding-history/', funding_history, name='funding_history'),
    path('receipt/<int:tx_id>/', transaction_receipt, name='receipt'),
    path("api/get-plans/", get_plans_view),
    path("api/buy_data/", buy_data_view),
    path("api/fund-wallet/", initialize_payment),
    path("receipt/<int:tx_id>/", transaction_receipt, name="receipt"),
    
    # ==================== AUTH VIEWS ====================
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),

    # ==================== PASSWORD RESET ====================
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='services/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='services/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='services/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='services/password_reset_complete.html'
    ), name='password_reset_complete'),

    # ==================== API V1 ====================
     path('api/v1/', include('services.api.api_urls')),

    # ==================== WEBHOOKS ====================
    path('payment/webhook/', paystack_webhook, name='paystack_webhook'),
]

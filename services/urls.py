from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("api/get-plans/", get_plans_view),
    path("api/buy_data/", buy_data_view),
    path("payment/webhook/", paystack_webhook),
    path("api/fund-wallet/", initialize_payment),
    path("receipt/<int:tx_id>/", transaction_receipt, name="receipt"),
    
    path("password-reset/", auth_views.PasswordResetView.as_view( template_name="services/password_reset.html"), name="password_reset" ),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view( template_name="services/password_reset_done.html" ), name="password_reset_done" ),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view( template_name="services/password_reset_confirm.html"), name="password_reset_confirm"),
    path( "reset/done/", auth_views.PasswordResetCompleteView.as_view( template_name="services/password_reset_complete.html" ), name="password_reset_complete"),
    
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),
]
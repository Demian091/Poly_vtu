from rest_framework import serializers
from django.contrib.auth import get_user_model
from services.models import Wallet, Transaction, WalletFunding, APIKey

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'profile_picture', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class WalletSerializer(serializers.ModelSerializer):
    """Wallet balance serializer"""
    class Meta:
        model = Wallet
        fields = ['balance']
        read_only_fields = ['balance']


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    created_at_formatted = serializers.DateTimeField(source='created_at', format='%b %d, %Y %I:%M %p', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'service', 'plan', 'phone', 'amount',
            'status', 'status_display', 'reference',
            'created_at', 'created_at_formatted'
        ]
        read_only_fields = fields


class WalletFundingSerializer(serializers.ModelSerializer):
    """Wallet funding serializer"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at_formatted = serializers.DateTimeField(source='created_at', format='%b %d, %Y %I:%M %p', read_only=True)

    class Meta:
        model = WalletFunding
        fields = ['id', 'amount', 'reference', 'status', 'status_display', 'created_at', 'created_at_formatted']
        read_only_fields = fields


class APIKeySerializer(serializers.ModelSerializer):
    """API Key serializer"""
    class Meta:
        model = APIKey
        fields = ['key', 'created_at', 'is_active']
        read_only_fields = fields


class DataPlanSerializer(serializers.Serializer):
    """Data plan from external API"""
    plan_id = serializers.CharField()
    name = serializers.CharField()
    price = serializers.CharField()
    validity = serializers.CharField()
    api_price = serializers.CharField()
    user_price = serializers.CharField()


class BuyDataRequestSerializer(serializers.Serializer):
    """Buy data request validator"""
    service = serializers.CharField(required=True)
    plan = serializers.CharField(required=True)
    phone = serializers.CharField(required=True, min_length=10, max_length=15)


class FundWalletRequestSerializer(serializers.Serializer):
    """Fund wallet request validator"""
    amount = serializers.IntegerField(required=True, min_value=100)


class PaystackInitializeResponseSerializer(serializers.Serializer):
    """Paystack initialize response"""
    authorization_url = serializers.URLField()


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        return data


class LoginSerializer(serializers.Serializer):
    """Login request serializer"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

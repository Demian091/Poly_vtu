from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings



class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True
)


class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return self.user.username


class Transaction(models.Model):

    TRANSACTION_TYPES = [
        ("credit", "Credit"),
        ("debit", "Debit")
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed")
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        default="debit"
    )

    service = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    plan = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - ₦{self.amount}"


class WalletFunding(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed")
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.reference
        
class APIKey(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    key = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = uuid.uuid4().hex + uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.key[:16]}..."
  
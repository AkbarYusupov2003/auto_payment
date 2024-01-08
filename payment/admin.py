from django.contrib import admin
from decimal import Decimal

from payment import models


@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("pk", "account_id", "number", "is_verified", "created_at", "updated_at", "is_deleted")
    list_filter = ("is_verified", "is_deleted", "created_at", "updated_at")


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_id", "status", "subscription_id", "amount", "auto_paid")
    list_filter = ("status", "subscription_id", "auto_paid", "created_at", "updated_at")


# -------------------------------------------------------------------------------
@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'username', 'get_amount', 'currency', 'payment_service', 'subscription_id', 'create_time', 'performed', 'transaction_id')
    list_display_links = "username",
    list_filter = ('performed', 'payment_service', 'currency',)
    search_fields = ('username',)
    ordering = ['-create_time']
    readonly_fields = 'username', 'amount', 'transaction_id', 'performed', 'payment_service', 'additional_parameters', "get_amount"

    def get_amount(self, obj=None):
        return Decimal(obj.amount/100).quantize(Decimal("0.00"))
    get_amount.short_description = "Сумма"


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "price", "archive")


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "balance")


@admin.register(models.IntermediateSubscription)
class IntermediateSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscription_type", "user", "date_of_debiting", "auto_payment")

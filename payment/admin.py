from django.contrib import admin

from payment import models


@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("pk", "account_id", "number", "expire", "created_at", "updated_at", "is_verified")
    list_filter = ("is_verified", "is_deleted", "created_at", "updated_at")


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_id", "status", "info", "amount", "auto_paid")
    list_filter = ("status", "info", "auto_paid", "created_at", "updated_at")


# -------------------------------------------------------------------------------
@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("pk", "transaction_id", "payment_service", "performed", "amount", "username", "create_time")


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "price", "archive")


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "balance")


@admin.register(models.IntermediateSubscription)
class IntermediateSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscription_type", "user", "date_of_debiting", "auto_payment")

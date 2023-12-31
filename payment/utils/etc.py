import datetime
from django.db.models import F

from payment.utils import data_extractor
from payment.utils import receipts
from payment import models


def is_paycom_card_exists(card_id, token):
    """Check if card with id and token exists in Paycom"""
    body = {
        "id": card_id,
        "method": "cards.check",
        "params": {
            "token": token
        }
    }
    response = data_extractor.get_data(body, secured=True)
    if response.get("result"):
        return True
    else:
        return False


def pay_by_card(
    card,
    amount,
    intermediate_subscription=None,
    auto_paid=False
):
    # TODO TEST
    account_id = card.account_id
    exists = is_paycom_card_exists(card.pk, card.token) if card else False
    if exists:
        try:
            account = models.Account.objects.get(pk=card.account_id)
        except:
            return False

        subscription = None
        subscription_id = None

        if intermediate_subscription:
            subscription = intermediate_subscription.subscription_type
            subscription_id = subscription.pk

        receipt = models.Receipt.objects.create(
            card=card,
            status=models.Receipt.StatusChoices.CREATED,
            amount=amount,
            auto_paid=auto_paid,
            subscription_id=subscription_id
        )
        transaction = models.Transaction.objects.create(
            transaction_id=receipt.receipt_id,
            payment_service="payme-card",
            amount=amount,
            additional_parameters=card.additional_data,
            username=account.username,
            account_id=account.pk,
            subscription_id=subscription_id,
            currency=models.Transaction.CurrencyChoices.uzs
        )
        receipt_id = receipts.create_receipt(receipt.pk, account_id, amount)
        if receipt_id:
            receipt.receipt_id = receipt_id
            receipt.save()
            paid = receipts.pay_receipt(receipt.pk, receipt_id, account_id, card.token)
            if paid:
                receipt.status = models.Receipt.StatusChoices.PAID
                receipt.save()

                transaction.performed = True
                transaction.transaction_id = receipt_id
                transaction.save()

                if not receipt.subscription_id:
                    # Пополнение баланса
                    account.balance = F("balance") + amount
                    account.save()
                else:
                    # Продление подписки
                    additional_parameters = {
                        "sub__id": subscription.pk,
                        "sub__title_ru": subscription.title_ru,
                        "transaction_id": transaction.pk,
                        "provider_transaction_id": receipt_id,
                    }
                    models.Transaction.objects.create(
                        amount=-amount,
                        performed=True,
                        transaction_id=receipt_id,
                        additional_parameters=additional_parameters,
                        payment_service="splay",
                        username=account.username,
                        account_id=account.pk,
                        subscription_id=subscription_id,
                        currency=models.Transaction.CurrencyChoices.uzs
                    )

                    if not intermediate_subscription.date_of_debiting:
                        intermediate_subscription.date_of_debiting = datetime.date.today() + datetime.timedelta(days=30)
                    else:
                        intermediate_subscription.date_of_debiting += datetime.timedelta(days=30)
                    intermediate_subscription.save()

                receipt.status = models.Receipt.StatusChoices.PAID
                receipt.save()
                return True
    return False

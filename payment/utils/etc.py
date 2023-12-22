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
    print("is_paycom_card_exists", response)
    if response.get("result"):
        return True
    else:
        return False


def pay_by_card(
    card,
    amount,
    subscription=None,
    auto_paid=False
):
    # TODO CHECK
    print("pay_by_card")
    account_id = card.account_id
    exists = is_paycom_card_exists(card.pk, card.token) if card else False
    if exists:
        if subscription:
            receipt = models.Receipt.objects.create(
                card=card,
                status=models.Receipt.StatusChoices.CREATED,
                subscription_id=subscription.pk,
                amount=amount,
                auto_paid=auto_paid
            )

        # models.Transaction.objects.create(
        #
        # )
        # TODO CREATE TRANSACTION with subscription

        receipt_id = receipts.create_receipt(receipt.pk, account_id, amount)
        print("RECEIPT ID", receipt_id)
        if receipt_id:
            receipt.receipt_id = receipt_id
            receipt.save()
            paid = receipts.pay_receipt(receipt.pk, receipt_id, account_id, card.token)
            if paid:
                # TODO UPDATE TRANSACTION
                receipt.status = models.Receipt.StatusChoices.PAID
                receipt.save()
                return True
    return False

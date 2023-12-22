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


def pay_by_card(card, price, info, auto_paid=False):
    # TODO CHECK
    print("pay_by_card")
    account_id = card.account_id
    exists = is_paycom_card_exists(card.pk, card.token) if card else False
    if exists:
        status = models.Receipt.StatusChoices.CREATED
        receipt = models.Receipt.objects.create(card=card, status=status, info=info, amount=price)
        receipt_id = receipts.create_receipt(receipt.pk, account_id, price)
        print("RECEIPT ID", receipt_id)
        if receipt_id:
            receipt.receipt_id = receipt_id
            receipt.save()
            paid = receipts.pay_receipt(receipt.pk, receipt_id, account_id, card.token)
            if paid:
                receipt.status = models.Receipt.StatusChoices.PAID
                receipt.auto_paid = auto_paid
                receipt.save()
                return True
    return False

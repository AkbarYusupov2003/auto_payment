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


def pay_by_card(instance, price):
    # TODO FIX EROR IF 2 IS VERIFIED AND 1 OF THEM DOESNT HAVE ENOUGH MONEY
    print("pay_by_card")
    account_id = instance.user.id
    card = models.Card.objects.filter(account_id=account_id, is_verified=True, auto_payment=True).first()
    print("Card", card)
    exists = is_paycom_card_exists(card.pk, card.token) if card else False
    if exists:
        print(1)
        status = models.Receipt.StatusChoices.CREATED
        info = instance.subscription_type.title_ru
        receipt = models.Receipt.objects.create(status=status, info=info, amount=price)
        receipt_id = receipts.create_receipt(receipt.pk, account_id, price)
        if receipt_id:
            print(2)
            receipt.receipt_id = receipt_id
            receipt.save()
            paid = receipts.pay_receipt(receipt.pk, receipt_id, account_id, card.token)
            if paid:
                print(3)
                receipt.status = models.Receipt.StatusChoices.PAID
                receipt.save()
                return True
    return False

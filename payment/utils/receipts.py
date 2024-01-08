from payment.utils import data_extractor


def create_receipt(pk, account_id, amount):
    body = {
        "id": pk,
        "method": "receipts.create",
        "params": {
            "amount": amount,
            "account": {
                "account_id": account_id
            },
        }
    }
    result = data_extractor.get_data(body).get("result")
    if result:
        return result.get("receipt").get("_id")
    else:
        return ""


def pay_receipt(pk, receipt_id, account_id, token):
    body = {
        "id": pk,
        "method": "receipts.pay",
        "params": {
            "id": receipt_id,
            "token": token,
            "payer": {
                "account_id": account_id
            }
        }
    }
    result = data_extractor.get_data(body, secured=True)
    if result.get("result"):
        return True
    else:
        return False

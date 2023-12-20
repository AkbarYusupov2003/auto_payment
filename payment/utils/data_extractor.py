import requests
from django.conf import settings


def get_data(body, secured=False):
    count = 1
    result = {}
    
    if secured:
        headers = {"X-Auth": f"{settings.PAYCOM_CASHBOX_ID}:{settings.PAYCOM_CASHBOX_KEY}"}
    else:
        headers = {"X-Auth": settings.PAYCOM_CASHBOX_ID}
    print("get_data")
    while count <= 3:
        # try:
            response = requests.post(settings.PAYCOM_API_URL, json=body, headers=headers)
            print("RR", response)
            result = response.json()
            print("GET DATA", response)
            break
        # except IOError as e:
        #     print("error", e)
        #     count += 1
    return result

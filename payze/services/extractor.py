import requests
from django.conf import settings


def get_data(body):
    count = 1
    result = {}

    headers = {"Authorization": f"{settings.PAYZE_API_KEY}:{settings.PAYZE_API_SECRET}"}
    while count <= 3:
        try:
            response = requests.post(settings.PAYCOM_API_URL, json=body, headers=headers)
            result = response.json()
            break
        except IOError as e:
            count += 1
    return result

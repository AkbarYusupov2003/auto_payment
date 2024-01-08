import re
import json
import datetime
from django.db.models import F
from django.shortcuts import HttpResponse, get_object_or_404
from django.views import View
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from payze import models
from payze import serializers
from payze.services import extractor


class ProductCreateAPIView(View):

    def get(self, request, *args, **kwargs):
        url = "https://payze.io/v2/api/product"
        body = {
            "name": "Подписка активация",
            "description": "Подписка активация",
            "imageUrl": "https://payze.io?imageId=12",
            "price": "35000",
            "currency": "UZS",
            "occurrenceType": "Day",
            "occurrenceNumber": "1",
            "occurrenceDuration": "10",
            "freeTrial": 5,
            "numberOfFailedRetry": 3
        }
        response = extractor.get_data(url, body)
        print("RESPONSE", response)
        # {
        #     "name": "Product Name",
        #     "description": "Product Description",
        #     "imageUrl": "https://payze.io?imageId=12",
        #     "price": "50",
        #     "currency": "GEL",
        #     "occurrenceType": "Day",
        #     "occurrenceNumber": "1",
        #     "occurrenceDuration": "10",
        #     "freeTrial": 5,
        #     "numberOfFailedRetry": 3
        # }

        return HttpResponse("Ok")

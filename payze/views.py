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
            "name": "Активация",
            "description": "Активация",
            "imageUrl": "",
            "price": "35000",
            "currency": "UZS",
            "occurrenceType": "Day",
            "occurrenceNumber": "30",
            "occurrenceDuration": "1",
            "freeTrial": 0,
            "numberOfFailedRetry": 1
        }
        response = extractor.get_data(url, body)
        print("RESPONSE", response)
        return HttpResponse("Ok")

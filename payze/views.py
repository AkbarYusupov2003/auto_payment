import re
import json
import datetime
from django.db.models import F
from django.shortcuts import HttpResponse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from payze import models
from payze import serializers
from payze.services import extractor


# 3104 - Setanta, 3105 - Активация

HOST = "https://b2d0-195-158-24-116.ngrok-free.app"


# Payment
class PaymentCreateAPIView(View):

    def get(self, request, *args, **kwargs):
        url = "https://payze.io/v2/api/payment"
        body = {
            "source": "Card",
            "amount": "1",
            "currency": "USD",
            "language": "RU",
            "hooks": {
                "webhookGateway": f"{HOST}/payze/payment/webhook",
                "successRedirectGateway": f"{HOST}/payze/payment/success",
                "errorRedirectGateway": f"{HOST}/payze/payment/error",
            },

        }
        # body = {
        #     "name": "Активация",
        #     "description": "Активация",
        #     "imageUrl": "",
        #     "price": "35000",
        #     "currency": "UZS",
        #     "occurrenceType": "Day",
        #     "occurrenceNumber": "30",
        #     "occurrenceDuration": "1",
        #     "freeTrial": 0,
        #     "numberOfFailedRetry": 1
        # }
        response = extractor.put_data(url, body)
        print("RESPONSE", response)
        return HttpResponse("Ok")


class PaymentWebhookGateway(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("Webhook Gateway: ", request.body)
        payze_response = json.loads(request.body)
        transaction_id = payze_response.get("paymentId")
        amount = payze_response.get("amount")
        print("amount", amount, type(amount))
        if transaction_id and amount:
            print("IN IF")
            url = "https://payze.io/v2/api/payment/capture"
            body = {
                "transactionId": transaction_id,
                "amount": amount
            }
            res = extractor.put_data(url, body)
            print("res", res)
        return HttpResponse("Webhook gateway")


class PaymentSuccessRedirectGateway(APIView):

    def get(self, request, *args, **kwargs):
        print("Success Gateway: ", request.body)
        return HttpResponse("Success redirect gateway")


class PaymentErrorRedirectGateway(APIView):

    def get(self, request, *args, **kwargs):

        return HttpResponse("Error redirect gateway")


# Products
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
        response = extractor.post_data(url, body)
        print("RESPONSE", response)
        return HttpResponse("Ok")


# Subscriptions
class SubscriptionCreateAPIView(APIView):

    def get(self, request, *args, **kwargs):
        url = "https://payze.io/v2/api/subscription"
        body = {
            "productId": 3105,
            "cardToken": "PAY123ZE...",
            "hookUrl": "https://payze.io",
            "email": "info@payze.ge",
            "phone": "+995...",
            "callback": "https://payze.io",
            "callbackError": "https://payze.io/error",
            "sendEmails": False
        }
        response = extractor.post_data(url, body)
        print("RESPONSE", response)
        return HttpResponse("Ok")

import json
from django.shortcuts import HttpResponse, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from payment.models import Transaction
from payze import models
from payze import serializers
from payze.services import extractor


# 3104 - Setanta, 3105 - Активация

HOST = "https://fa4c-195-158-24-116.ngrok-free.app"


# Payment
class PaymentCreateAPIView(View):

    def get(self, request, *args, **kwargs):
        url = "https://payze.io/v2/api/payment"
        amount = 1000
        body = {
            "source": "Card",
            "amount": amount,
            "currency": "UZS",
            "language": "RU",
            "hooks": {
                "webhookGateway": f"{HOST}/payze/payment/webhook",
                "successRedirectGateway": f"{HOST}/payze/payment/success",
                "errorRedirectGateway": f"{HOST}/payze/payment/error",
            },
            "cardPayment": {
                "tokenizeCard": True
            }
        }
        payze_response = extractor.put_data(url, body).get("data").get("payment")
        Transaction.objects.create(
            # TODO create with more fields
            amount=amount,
            transaction_id=payze_response.get("transactionId"),
            additional_parameters={
                "payment_id": payze_response.get("id"),
                "token": payze_response.get("cardPayment").get("token")
            },
            payment_service="payze-card",
            performed=False
        )
        to_url = payze_response.get("paymentUrl")
        return redirect(to_url)


class PaymentWebhookGateway(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("Payment Webhook Gateway: ", request.body)
        payze_response = json.loads(request.body)
        transaction = get_object_or_404(
            Transaction, transaction_id=payze_response.get("PaymentId")
        )
        transaction.performed = True
        transaction.save()
        return HttpResponse("Webhook gateway")


class PaymentSuccessRedirectGateway(APIView):

    def get(self, request, *args, **kwargs):
        print("Success Gateway: ", request.body)
        return HttpResponse("Success redirect gateway")


class PaymentErrorRedirectGateway(APIView):

    def get(self, request, *args, **kwargs):
        print("Error Gateway: ", request.body)
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
            "cardToken": "89EAC3569B8A4632AFB2372BA",
            "hookUrl": f"{HOST}/payze/subscriptions/webhook",
            "email": "akbarbek.yusupov@gmail.com",
            #"phone": "+995...",
            #"callback": f"{HOST}/payze/success/webhook",
            #"callbackError": f"{HOST}/payze/error/webhook",
            #"sendEmails": False
        }
        response = extractor.post_data(url, body)
        print("RESPONSE", response)
        return HttpResponse("Ok")


class SubscriptionWebhookAPIViewGateway(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("Subscription Webhook Gateway: ", request.body)
        payze_response = json.loads(request.body)
        # TODO Create transaction for paid subscription
        return HttpResponse("Webhook gateway")

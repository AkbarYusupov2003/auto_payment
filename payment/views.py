import re
import json
import datetime
from django.db.models import F
from django.shortcuts import HttpResponse, get_object_or_404
from django.views import View
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from payment import models
from payment import serializers
from payment.utils import data_extractor, tokens, etc


# Move to Frontend
class MainView(View):
    # TODO for Frontend: generate id -> from user_id...
    def get(self, request, *args, **kwargs):
        card_id = 1 # models.Card.objects.all().last().pk + 1
        body = {
            "id": card_id,
            "method": "cards.create",
            "params": {
                "card": {"number": "8600069195406311", "expire": "0399"},
                "save": True
            }
        }
        response = data_extractor.get_data(body)
        print("Main response", response)
        data = response.get("result").get("card")
        return HttpResponse(f"data: {data}")


TOKEN = "658437dd448046c31012c140_7ikvwpEVaY0jZQI3X7tygzIvtmGEYy4KHzjgvGkb2MHFK3u6YcWwanvqyWixXpYys2t3MGDIyGz16E5Ho5kIrkNIxG2FdTASRt5HwzCNDDbiVxdgjg21DdN4NP6SgQTwZzBxxmPCTbk636ckm9WO6OQBX4B2nddeEF3jkUrZw13B8Xh62HWsSuo98axCZhCSXK2sq48dQKj8RKIvKfAXbqWbynanPDVVgT9H9QOqeBSWipEZi6fuGYAEUtYsIP8BYsO88Hbbn55qSQz6cw3F7yePy0fe8FFHAVcqQpZkyCDQACGJwy3QuAOVTzEwXAGVMW1MDrVMsvFsd39GGxpNnxoSEI9AbGazybpA2Y8ReFh72TVpTnYazT9MxdpEdZmKOyXMnw"
PK = 1


class CardGetVerifyCode(View):

    def get(self, request, *args, **kwargs):
        body = {
            "id": PK,
            "method": "cards.get_verify_code",
            "params": {
                "token": TOKEN
            }
        }
        response = data_extractor.get_data(body)
        print("Get code response", response)
        return HttpResponse("Get Verify Code")


class CardVerify(View):

    def get(self, request, *args, **kwargs):
        body = {
            "id": PK,
            "method": "cards.verify",
            "params": {
                "token": TOKEN,
                "code": "666666"
            }
        }
        response = data_extractor.get_data(body)
        print("Verify response", response)
        return HttpResponse("Verify")
# Move to Frontend ended


class CardListAPIView(generics.ListAPIView):
    serializer_class = serializers.CardListSerializer
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        try:
            splay_data = tokens.get_data_from_token(self.request.META["HTTP_AUTHORIZATION"])
            account_id = int(splay_data.get("user_id"))
            return models.Card.objects.filter(account_id=account_id, is_deleted=False)
        except:
            return []


class CardCreateAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            splay_data = tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            account_id = int(splay_data["user_id"])
        except:
            return Response({"error": ""}, status=401)
        # -----------------------------------------------------------------------------------------
        if models.Card.objects.filter(account_id=account_id, is_deleted=False).count() < 10:
            card = models.Card.objects.create(account_id=account_id)
            return Response({"message": "The card was successfully created", "id": card.pk}, status=201)
        else:
            return Response({"error": "Account already has 10 cards"}, status=405)


class CardRetrieveAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            account_id = int(tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"]).get("user_id"))
            account_id = 1 # TODO REMOVE
        except:
            return Response({"error": ""}, status=401)
        # -----------------------------------------------------------------------------------------
        try:
            data = json.loads(request.body)
            card_id = int(self.kwargs["card_id"])
            token = str(data["token"])
            additional_data = dict(data["additional_data"])
            auto_payment = data.get("auto_payment")
        except:
            return Response({"error": "Data validation error"}, status=401)
        # -----------------------------------------------------------------------------------------
        get_object_or_404(models.Account, pk=account_id)
        card = get_object_or_404(models.Card, pk=card_id, account_id=account_id, is_deleted=False)
        if etc.is_paycom_card_exists(card.pk, token):
            if not card.is_verified:
                card.token = token
                card.number = additional_data.get("number")
                card.expire = additional_data.get("expire")
                card.additional_data = additional_data
                card.is_verified = True
            if isinstance(auto_payment, bool):
                card.auto_payment = auto_payment
                card.save()
        else:
            card.token = token
            number = additional_data.get("number")
            expire = additional_data.get("expire")
            if re.match(r"^(9860|8600|5614)[0-9]{2}(\*){6}[0-9]{4}$", number):
                card.number = number
            if re.match(r"^(0[1-9]|1[0-2])/(2[3-9]|[3-9][0-9])$", expire):
                card.expire = expire
            card.additional_data = additional_data
            card.save()

        return Response({"message": "The card was successfully updated"}, status=200)

    def delete(self, request, *args, **kwargs):
        try:
            splay_data = tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            account_id = int(splay_data.get("user_id"))
            account_id = 1  # TODO REMOVE
        except:
            return Response({"error": ""}, status=401)
        # -----------------------------------------------------------------------------------------
        try:
            card_id = int(self.kwargs["card_id"])
        except:
            return Response({"error": "Data validation error"}, status=401)
        # -----------------------------------------------------------------------------------------
        card = get_object_or_404(models.Card, pk=card_id, account_id=account_id)
        card.is_deleted = True
        card.save()
        return Response({"message": "The card is successfully deleted"}, status=200)


class RefillBalanceAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            splay_data = tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            account_id = int(splay_data.get("user_id"))
            account_id = 1  # TODO REMOVE
        except:
            return Response({"error": ""}, status=401)
        # -----------------------------------------------------------------------------------------
        try:
            data = json.loads(request.body)
            card_id = int(data["card_id"])
            amount = int(data["amount"])
            if not (amount > 0):
                raise Exception("amount not positive")
        except:
            return Response({"error": "Data validation error"}, status=401)
        account = get_object_or_404(models.Account, pk=account_id)
        card = get_object_or_404(models.Card, pk=card_id, account_id=account_id, is_verified=True, is_deleted=False)
        # -----------------------------------------------------------------------------------------
        paid = etc.pay_by_card(card=card, amount=amount)
        if paid:
            account.balance = F("balance") + amount
            account.save()
            return Response({"message": "Refill operation succeeded"}, status=200)
        else:
            return Response({"error": "Refill operation failed"}, status=406)


class SubscriptionPaymentAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            splay_data = tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            account_id = int(splay_data.get("user_id"))
            account_id = 1  # TODO REMOVE
        except:
            return Response({"error": ""}, status=401)
        # -----------------------------------------------------------------------------------------
        try:
            card_id = int(data["card_id"])
            sub_id = int(data["sub_id"])
        except:
            return Response({"error": "Data validation error"}, status=401)
        card = get_object_or_404(models.Card, pk=card_id, account_id=account_id, is_verified=True, is_deleted=False)
        subscription = get_object_or_404(models.Subscription, pk=sub_id)
        # -----------------------------------------------------------------------------------------
        today = datetime.date.today()
        try:
            instance = models.IntermediateSubscription.objects.get(
                user_id=account_id, subscription_type=subscription, date_of_debiting__gte=today
            )
        except models.IntermediateSubscription.DoesNotExist:
            models.IntermediateSubscription.objects.filter(subscription_type=subscription, user_id=account_id).delete()
            instance = models.IntermediateSubscription.objects.create(subscription_type=subscription, user_id=account_id)
        # -----------------------------------------------------------------------------------------
        paid = etc.pay_by_card(
            subscription=instance,
            card=card,
            amount=subscription.price,
        )
        if paid:
            if not instance.date_of_debiting:
                instance.date_of_debiting = today + datetime.timedelta(days=30)
            else:
                instance.date_of_debiting += datetime.timedelta(days=30)
            instance.save()
            return Response({"message": "subscription paid"}, status=200)
        else:
            return Response({"error": "subscription was not paid"}, status=406)

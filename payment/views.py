import json
import datetime
from django.conf import settings
from django.shortcuts import HttpResponse, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from payment import models
from payment import serializers
from payment.utils import data_extractor, token, etc


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
        card_id = response.get("id")
        data = response.get("result").get("card")
        token = data.pop("token", "not exists")
        models.Card.objects.create(pk=card_id, account_id=1, token=token, additional_data=data)
        return HttpResponse(f"token: {token}")


class CardGetVerifyCode(View):
    
    def get(self, request, *args, **kwargs):
        card = models.Card.objects.all().last()
        body = {
            "id": card.pk,
            "method": "cards.get_verify_code",
            "params": {
                "token": card.token
            }
        }
        response = data_extractor.get_data(body)
        print("Get code response", response)
        return HttpResponse("Get Verify Code")


class CardVerify(View):
    
    def get(self, request, *args, **kwargs):
        card = models.Card.objects.all().last()
        body = {
            "id": card.pk,
            "method": "cards.verify",
            "params": {
                "token": card.token,
                "code": "666666"
            }
        }
        response = data_extractor.get_data(body)
        print("Verify response", response)
        return HttpResponse("Verify")
# Move to Frontend ended


# create with fields: account_id, card_id, token, additional_data (is_active=False)
# updatable fields: additional_data, auto_payment, is_active


class CardCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            splay_data = token.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            account_id = int(splay_data.get("user_id"))
            # check if account account_has_less_than_10_cards
        except:
            return Response({"error": "token authorization error"}, status=401)
        return models.Card.objects.create(account_id=account_id).pk


class CardUpdateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            account_id = int(data["account_id"])
            card_id = int(data["card_id"])
            token = str(data["token"])
            additional_data = dict(data["additional_data"])
        except:
            return Response({"Data validation error"}, status=400)

        # check if account exists
        # check if token exists

        account = get_object_or_404(models.Account, pk=account_id)
        if etc.is_paycom_card_exists(card_id, token):
            # TODO UPDATE EXISTINS CARD
            pass
            # models.Card.objects.create(
            #     pk=card_id, account_id=account_id,
            # )

        # create card

        return Response({"message": "The card was successfully created"}, status=201)


class CardListAPIView(generics.ListAPIView):

    def get_queryset(self):
        return models.Card.objects.all()


# TODO AccountCardList

class BuySubscriptionAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        sub_id = body.get("sub_id")
        account_id = body.get("account_id")
        card_id = body.get("card_id")
        
        if type(sub_id) == int and type(account_id) == int and type(card_id) == int:
            get_object_or_404(models.Account, pk=account_id)
            get_object_or_404(models.Card, pk=card_id, account_id=account_id)
            allowed_subs = models.Subscription.objects.all().values_list("pk", flat=True)
            if not (sub_id in allowed_subs):
                return Response({"error": "sub_id validation"}, status=400)
            today = datetime.datetime.today()
            instance = models.IntermediateSubscription.objects.filter(
                subscription_type_id=sub_id, user_id=account_id, date_of_debiting__gte=today
            ).first()
            if instance:
                paid = etc.pay_by_card(instance, instance.subscription_type.price)
                if paid:
                    instance.date_of_debiting += datetime.timedelta(days=30)
                    instance.save()
                    return Response({"message": "subscription paid"}, status=200)
            else:
                instance = models.IntermediateSubscription.objects.create(
                    subscription_type_id=sub_id, user_id=account_id
                )
                paid = etc.pay_by_card(instance, instance.subscription_type.price)
                if paid:
                    instance.date_of_debiting = today + datetime.timedelta(days=30)
                    instance.save()
                    return Response({"message": "subscription paid"}, status=200)

            return Response({"error": "subscription was not paid"}, status=200)
        else:
            return Response({"error": "numeric validation"}, status=400)

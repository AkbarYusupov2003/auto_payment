import json
import datetime
from django.conf import settings
from django.shortcuts import HttpResponse, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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
        card_id = 7 # models.Card.objects.all().last().pk + 1
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
        token = response.get("result").get("card").get("token")
        print(response.get("result"))
        # models.Card.objects.create(pk=card_id, account_id=1, token=token, additional_data=data)
        return HttpResponse(f"data: {data}")


TOKEN = "6583d8a4448046c31012c123_E0i0hYKJ8tT5BMJUzvm6ixe8DXewezWjsUr6StNMQH1NK7r3cOgeBwSTotauq97VWyNfty3OTMz3mJNG42g0GjfpYPHWJb5PaQ3EGU0EZYNj8nhFggfuQcuf2YpDie2rfzKoVaUtmGankcIFmCBBwAPbWnNNaUNJMzfmwgkjyJxuVvdEUDRz8N5fEYkpctuhKgzsy9Ir9VhxG4JHX2tBb6rRPg4uQPwRnUwpvdPz0YnptKnOCNti19emxecjzUBYWFQagBRxKTqd1N8tjoOBzBogrzIMjDaqnROyBr9g0JBPr3DRjVEFY6b1gcpiQv1oh2smwmqYmMQujh1Ozwcdx5ritSvT0waH6z9TjbjResd1ZJc6H99QQoYBuZZ1qv8bV18nOn"


class CardGetVerifyCode(View):

    def get(self, request, *args, **kwargs):
        card = models.Card.objects.all().last()
        body = {
            "id": card.pk,
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
        card = models.Card.objects.all().last()
        body = {
            "id": card.pk,
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


class CardCreateAPIView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # try:
        #     splay_data = tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
        #     account_id = json.loads(request.body)["account_id"]
        #     if not (account_id == int(splay_data["user_id"])):
        #         raise Exception("")
        # except Exception as e:
        #     print("exception", e)
        #     return Response({"error": "token, account_id does not match"}, status=401)
        account_id = json.loads(request.body)["account_id"]
        if models.Card.objects.filter(account_id=account_id).count() < 10:
            card = models.Card.objects.create(account_id=account_id)
            return Response({"message": "The card was successfully created", "id": card.pk}, status=201)
        else:
            return Response({"error": "Account already has 10 cards"}, status=405)


# create with fields: account_id, card_id, is_verified=False
class CardUpdateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        try:
            account_id = int(data["account_id"])
            # splay_data = tokens.get_data_from_token(request.META["HTTP_AUTHORIZATION"])
            # if not (int(splay_data.get("user_id")) == account_id):
            #     raise Exception("")
            card_id = int(self.kwargs["card_id"])
            card_token = str(data["token"])
            additional_data = dict(data["additional_data"])
            auto_payment = data.get("auto_payment")
        except Exception as e:
            return Response({"error": "Data validation error"}, status=400)

        get_object_or_404(models.Account, pk=account_id)
        cards = models.Card.objects.filter(pk=card_id, account_id=account_id)
        exists = False
        for card in cards:
            if etc.is_paycom_card_exists(card.pk, card_token):
                if not card.is_verified:
                    card.token = card_token
                    card.number = additional_data.get("number")
                    card.expiration = additional_data.get("expire")
                    card.additional_data = additional_data
                    card.is_verified = True
                if isinstance(auto_payment, bool):
                    card.auto_payment = auto_payment
                    card.save()
                exists = True
                break
        if exists:
            return Response({"message": "The card was successfully updated"}, status=200)
        else:
            return Response({"error": "Card not found"}, status=404)


class CardListAPIView(generics.ListAPIView):
    serializer_class = serializers.CardListSerializer

    def get_queryset(self):
        account_id = self.kwargs["account_id"]
        return models.Card.objects.filter(account_id=account_id)


class BuySubscriptionAPIView(APIView):

    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        sub_id = body.get("sub_id")
        account_id = body.get("account_id")
        card_id = body.get("card_id")
        # TODO isinstance
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

from rest_framework import serializers

from payment import models


class CardCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Card
        fields = ("account_id", "card_id", "token", "additional_data")
        

class CardUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Card
        fields = ("additional_data", "auto_payment", "auto_payment", "is_active")

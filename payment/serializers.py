from rest_framework import serializers

from payment import models


class CardListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Card
        fields = ("pk", "token", "number", "expire", "is_verified", "auto_payment", "updated_at")

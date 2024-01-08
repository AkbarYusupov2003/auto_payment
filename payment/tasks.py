import datetime
from django.db.models import Q
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from payment import models
from payment.utils import etc


@shared_task(name="daily-subscription-task")
def daily_subscription_task():
    today = datetime.datetime.today()
    models.IntermediateSubscription.objects.filter(
        Q(date_of_debiting__lt=today) | Q(date_of_debiting__isnull=True)
    ).delete()
    to_extend = models.IntermediateSubscription.objects.filter(
        auto_payment=True, date_of_debiting=today
    ).select_related("subscription_type", "user")
    extended = []
    tomorrow = models.IntermediateSubscription.objects.filter(date_of_debiting=today + datetime.timedelta(days=1))
    day_after_tomorrow = models.IntermediateSubscription.objects.filter(date_of_debiting=today + datetime.timedelta(days=2))

    for intermediate_subscription in to_extend:
        print("subscription", intermediate_subscription)

        if intermediate_subscription.subscription_type.archive:
            intermediate_subscription.delete()
            continue

        price = intermediate_subscription.subscription_type.price
        if intermediate_subscription.user.balance >= price:
            user = intermediate_subscription.user
            subscription = intermediate_subscription.subscription_type

            user.balance -= price
            user.save()

            intermediate_subscription.date_of_debiting += datetime.timedelta(days=30)
            intermediate_subscription.save()
            extended.append(subscription)

            additional_parameters = {
                "sub__id": subscription.pk,
                "sub__title_ru": subscription.title_ru,
                "transaction_id": None,
                "provider_transaction_id": None,
            }
            models.Transaction.objects.create(
                amount=-price,
                performed=True,
                transaction_id=None,
                additional_parameters=additional_parameters,
                payment_service="splay",
                username=user.username,
                account_id=user.pk,
                subscription_id=subscription.pk,
                currency=models.Transaction.CurrencyChoices.uzs
            )
        else:
            cards = models.Card.objects.filter(
                account_id=intermediate_subscription.user_id, is_verified=True, auto_payment=True, is_deleted=False
            )
            paid = False
            for card in cards:
                if etc.pay_by_card(
                    card=card, amount=price, intermediate_subscription=intermediate_subscription, auto_paid=True
                ):
                    paid = True
                    intermediate_subscription.date_of_debiting += datetime.timedelta(days=30)
                    intermediate_subscription.save()
                    extended.append(intermediate_subscription)
                    break

            if not paid:
                intermediate_subscription.delete()

    return {"extended": extended, "tomorrow": tomorrow, "day_after_tomorrow": day_after_tomorrow}


app.conf.beat_schedule = {
    "daily-subscription-task": {
        "task": "daily-subscription-task",
        "schedule": crontab(hour="0", minute="1"),
    },
}

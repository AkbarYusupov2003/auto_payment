import datetime
from django.db.models import Q
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from payment import models
from payment.utils import etc


@shared_task(name="daily-subscription-task")
def daily_subscription_task():
    today = datetime.datetime.now()
    models.IntermediateSubscription.objects.filter(
        Q(date_of_debiting__lt=today) | Q(date_of_debiting__isnull=True)
    ).delete()
    to_extend = models.IntermediateSubscription.objects.filter(
        auto_payment=True, date_of_debiting=today
    ).select_related("subscription_type", "user")
    extended = []
    tomorrow = models.IntermediateSubscription.objects.filter(date_of_debiting=today + datetime.timedelta(days=1))
    day_after_tomorrow = models.IntermediateSubscription.objects.filter(date_of_debiting=today + datetime.timedelta(days=2))

    for subscription in to_extend:
        print("subscription", subscription)

        if subscription.subscription_type.archive:
            subscription.delete()
            continue

        price = subscription.subscription_type.price
        if subscription.user.balance >= price:
            subscription.user.balance -= price
            subscription.user.save()
            subscription.date_of_debiting += datetime.timedelta(days=30)
            subscription.save()
            extended.append(subscription)
        else:
            cards = models.Card.objects.filter(
                account_id=subscription.user_id, is_verified=True, auto_payment=True, is_deleted=False
            )
            paid = False
            for card in cards:
                if etc.pay_by_card(
                    card=card, amount=price, subscription=subscription, auto_paid=True
                ):
                    paid = True
                    subscription.date_of_debiting += datetime.timedelta(days=30)
                    subscription.save()
                    extended.append(subscription)
                    break

            if not paid:
                subscription.delete()

    return {"extended": extended, "tomorrow": tomorrow, "day_after_tomorrow": day_after_tomorrow}


app.conf.beat_schedule = {
    "daily-subscription-task": {
        "task": "daily-subscription-task",
        "schedule": crontab(hour="0", minute="1"),
    },
}

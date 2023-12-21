import datetime
from celery import shared_task
from celery.schedules import crontab

from config.celery import app
from payment import models
from payment.utils import etc
from payment.utils import receipts


@shared_task(name="daily-subscription-task")
def daily_subscription_task():
    # TODO Deleting old subs - ??? models.IntermediateSubscription.objects.filter(date_of_debiting__date__lt=today).delete()
    today = datetime.datetime.now()
    to_extend = models.IntermediateSubscription.objects.filter(
        auto_payment=True, date_of_debiting=today
    ).select_related("subscription_type", "user")
    extended = []
    tomorrow = models.IntermediateSubscription.objects.filter(date_of_debiting=today + datetime.timedelta(days=1))
    day_after_tomorrow = models.IntermediateSubscription.objects.filter(date_of_debiting=today + datetime.timedelta(days=2))

    for instance in to_extend:
        print("instance", instance)

        if instance.subscription_type.archive:
            instance.delete()
            continue

        price = instance.subscription_type.price
        if instance.user.balance >= price:
            instance.user.balance -= price
            instance.user.save()
            instance.date_of_debiting += datetime.timedelta(days=30)
            instance.save()
            extended.append(instance)
        else:
            cards = models.Card.objects.filter(account_id=instance.user_id, is_verified=True, auto_payment=True)
            info = instance.subscription_type.title_ru
            paid = False
            for card in cards:
                if etc.pay_by_card(card, price, info, auto_paid=True):
                    paid = True
                    instance.date_of_debiting += datetime.timedelta(days=30)
                    instance.save()
                    extended.append(instance)
                    break

            if not paid:
                instance.delete()

    return {"extended": extended, "tomorrow": tomorrow, "day_after_tomorrow": day_after_tomorrow}


app.conf.beat_schedule = {
    "daily-subscription-task": {
        "task": "daily-subscription-task",
        "schedule": crontab(hour="0", minute="1"),
    },
}

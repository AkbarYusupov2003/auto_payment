from django.db import models


gettext = lambda s: s
langs = (
    ('ru', gettext('Russian')),
    ('en', gettext('English')),
    ('uz', gettext('Uzbek')),
)


class Card(models.Model):
    account_id = models.PositiveIntegerField("ID Аккаунта")
    token = models.CharField("Токен", max_length=512)
    #
    number = models.CharField("Номер", max_length=32, null=True)
    expire = models.CharField("Срок истечения", max_length=16, null=True)
    additional_data = models.JSONField("Дополнительная информация", default=dict)
    #
    auto_payment = models.BooleanField("Авто оплата", default=True)
    is_verified = models.BooleanField("Верифицирована", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Карта"
        verbose_name_plural = "Карты"


class Receipt(models.Model):
    class StatusChoices(models.TextChoices):
        # TODO mb add not enough money status or smth
        CREATED = "CREATED", "Создан"
        FAILED = "FAILED", "Ошибка"
        PAID = "PAID", "Оплачен"

    account_id = models.PositiveIntegerField("ID Аккаунта")
    receipt_id = models.CharField("ID Чека", max_length=32, unique=True)
    status = models.CharField("Статус", choices=StatusChoices.choices)
    info = models.CharField("Информация", max_length=128)
    amount = models.IntegerField("Сумма")
    auto_paid = models.BooleanField("Оплачен автоматический", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"


# -------------------------------------------------------------------------------
class Transaction(models.Model):
    PAYMENT_SERVICES = (
        ("splay", "Splay"),
        ("octo", "Octo"),
    )

    amount = models.BigIntegerField("Сумма в тийинах")
    additional_parameters = models.JSONField("Дополнительные параметры", default=dict, blank=True, null=True)
    payment_service = models.CharField("Платежная служба", max_length=10, choices=PAYMENT_SERVICES, blank=True, null=True)
    transaction_id = models.CharField("Provider transction ID", max_length=36, blank=True, null=True)
    performed = models.BooleanField("Выполнен", default=False)
    create_time = models.DateTimeField("Время создания", auto_now_add=True)
    # Payment details:
    username = models.CharField("Пользователь", max_length=60)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"


class Subscription(models.Model):
    for iso in langs:
        locals()[f'title_{iso[0]}'] = models.CharField(f'Название на [{iso[1]}]', max_length=60)
        locals()[f'description_{iso[0]}'] = models.CharField(f'Описание на [{iso[1]}]', max_length=500)
        locals()[f'description_list_{iso[0]}'] = models.TextField(f'Описание на [{iso[1]}]', max_length=1500, null=True, blank=True)

    limit_sessions = models.PositiveSmallIntegerField('Лимит сессий', default=3)
    price = models.PositiveIntegerField('Цена подписки в месяц в тийинах')
    ordering = models.PositiveSmallIntegerField("Позиция в списке", default=10)
    # color = ColorField('Цвет', blank=True, null=True)
    # icon = models.ImageField("Icon", blank=True, null=True, help_text='Ширина и высота Icon должна быть 100x100px')
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.title_ru

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Account(models.Model):
    username = models.CharField(max_length=60, unique=True, error_messages={'unique': 'username must be unique'})
    balance = models.PositiveBigIntegerField('Баланс в тийинах', default=0)

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'


class IntermediateSubscription(models.Model):
    subscription_type = models.ForeignKey(Subscription, related_name='users', on_delete=models.CASCADE)
    user = models.ForeignKey(Account, related_name='subscriptions', on_delete=models.CASCADE)
    date_of_debiting = models.DateField('Дата следующего списания', null=True, blank=True)
    auto_payment = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscription_type', 'user'], name='Unique Subscription Type'
            ),
        ]
        verbose_name = "Промежуточная модель подписок"
        verbose_name_plural = "Промежуточная модель подписок"

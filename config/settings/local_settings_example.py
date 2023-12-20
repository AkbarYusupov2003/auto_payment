SECRET_KEY = "123" 
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "auto_payment",
        "USER": "postgres",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

PAYCOM_API_URL = "https://checkout.test.paycom.uz/api"
PAYCOM_CASHBOX_ID = ""
PAYCOM_CASHBOX_KEY = ""
PAYCOM_CASHBOX_TEST_KEY = ""

CELERY_BROKER_URL = "redis://localhost:6379"

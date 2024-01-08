from django.contrib import admin
from django.urls import path, include

from config.yasg import urlpatterns as yasg_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("payment.urls", namespace="payment")),
    path("payze/", include("payze.urls")),
]

urlpatterns.extend(yasg_urls)

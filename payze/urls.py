from django.urls import path

from payze import views


urlpatterns = [
    # Payment
    path("payment/create", views.PaymentCreateAPIView.as_view()),
    # hooks
    path("payment/webhook", views.PaymentWebhookGateway.as_view()),
    path("payment/success", views.PaymentSuccessRedirectGateway.as_view()),
    path("payment/error", views.PaymentErrorRedirectGateway.as_view()),

    # Products
    # path("products/", views.ProductListAPIView.as_view()),
    path("products/create", views.ProductCreateAPIView.as_view()),

    # Subscriptions
    path("subscriptions/create", views.SubscriptionCreateAPIView.as_view()),
    path("subscriptions/", views.SubscriptionCreateAPIView.as_view()),
]

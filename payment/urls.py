from django.urls import path

from payment import views


app_name = "payment"

urlpatterns = [
    # Move to Frontend
    path("main/", views.MainView.as_view()),
    path("get-verify-code/", views.CardGetVerifyCode.as_view()),
    path("verify/", views.CardVerify.as_view()),
    #
    path("cards/", views.CardListAPIView.as_view()),
    path("cards/create/", views.CardCreateAPIView.as_view()),
    path("cards/<int:card_id>/", views.CardUpdateAPIView.as_view()),
    #
    path("refill-balance/", views.RefillBalanceAPIView.as_view()), # TODO
    path("subscription-payment/", views.SubscriptionPaymentAPIView.as_view()),
]

from django.urls import path

from payment import views


app_name = "payment"

urlpatterns = [
    # Move to Frontend
    path("main/", views.MainView.as_view()),
    path("get-verify-code/", views.CardGetVerifyCode.as_view()),
    path("verify/", views.CardVerify.as_view()),
    #
    # create
    # update with activation
    path("card/create/", views.CardCreateAPIView.as_view()),
    path("card/<int:card_id>/", views.CardUpdateAPIView.as_view()),
    # TODO path("card/<int:pk>/", views.CardUpdateAPIView.as_view()),
    # TODO path("card-list/", views.CardListAPIView.as_view()),
    
    path("buy-subscription/", views.BuySubscriptionAPIView.as_view()),
]

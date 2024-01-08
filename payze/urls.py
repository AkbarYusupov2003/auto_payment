from django.urls import path

from payze import views


urlpatterns = [
    path("products/create", views.ProductCreateAPIView.as_view()),
]

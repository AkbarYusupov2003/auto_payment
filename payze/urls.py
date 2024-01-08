from django.urls import path

from payze import views


urlpatterns = [
    path("", views.TestAPIView.as_view()),
]

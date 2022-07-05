from django.urls import path
from . import views

urlpatterns = [
    path('my-account', views.myaccount, name="my-account"),
    path('change-password', views.changepassword, name="change-password"),
]

from django.urls import path
from . import views

urlpatterns = [
    path('email-logs/', views.email_logs, name="email-logs"),
    path('sms-logs/', views.sms_logs, name="sms-logs")
    ]
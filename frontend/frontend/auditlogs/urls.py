from django.urls import path
from . import views

urlpatterns = [
    path('', views.auditlogs, name="audit-logs"),
]

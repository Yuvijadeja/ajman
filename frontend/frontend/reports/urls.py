from django.urls import path
from . import views

urlpatterns = [
    path('average/', views.average, name="average"),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.stations, name="station-status"),
    path('parameters', views.parameters, name="parameters"),
    path('get-stations/', views.getStation, name="get-stations"),
    path('get-parameters/', views.getParameters, name="get-parameters"),
]

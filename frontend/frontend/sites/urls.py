from django.urls import path
from . import views

urlpatterns = [
    path('map-view', views.map, name="map-view"),
    path('get-sites/', views.getSites, name="get-sites"),
    path('get-stations/', views.getStation, name="get-stations"),
    path('get-parameters/', views.getParameters, name="get-parameters"),
    path('get-parameters-values/', views.get_parameters_values, name="get-parameters-values"),


]

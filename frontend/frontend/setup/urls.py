from django.urls import path

from setup import views
from . import views

urlpatterns = [
    path('',views.setup,name='set-up')

]

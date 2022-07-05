from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name="login"),
    path('', views.realtimedata, name="realtime-data"),
    # path('', views.home, name="home"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('dashboard/setup', views.dashboardsetup, name="dashboard-setup"),
    path('delete-widget', views.delWidget, name="delete-widget"),
    path('logout', views.logout, name="logout"),
]

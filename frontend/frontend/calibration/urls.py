from django.urls import path
from . import views

urlpatterns = [
    path('remote-calibration/', views.remotecalibration, name="remote-calibration"),
    path('activate-calibration/', views.activateCalibration, name="activate-calibration"),
    path('calibration-logs/', views.calibrationlogs, name="calibration-logs"),
]

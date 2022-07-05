from django.urls import path
from . import views

urlpatterns = [
    path('multi-axis/', views.multi_axis_report, name="multi-axis"),
    path('matrix-report/', views.matrix_report, name="matrix-report"),
]

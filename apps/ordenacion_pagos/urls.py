from django.urls import path
from . import views

app_name = 'ordenacion_pagos'

urlpatterns = [
    path('', views.dashboard_ordenacion, name='dashboard'),
    path('crear/', views.solicitud_create, name='solicitud_create'),
    path('autorizar/<int:pk>/', views.autorizar_pago, name='autorizar_pago'),
]

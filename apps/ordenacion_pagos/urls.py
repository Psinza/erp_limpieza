from django.urls import path
from . import views

app_name = 'ordenacion_pagos'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
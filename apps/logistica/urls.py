from django.urls import path
from . import views

app_name = 'logistica'

urlpatterns = [
    path('kardex/', views.reporte_kardex, name='reporte_kardex'),
    path('transferencia/nueva/', views.registrar_transferencia, name='registrar_transferencia'),
]
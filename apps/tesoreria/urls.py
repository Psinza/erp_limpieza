from django.urls import path
from . import views

app_name = 'tesoreria'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cuentas-cobrar/', views.cxc_list, name='cxc_list'),
    path('cuentas-cobrar/nueva/', views.cxc_create, name='cxc_create'),
    path('cuentas-cobrar/<int:pk>/', views.cxc_detail, name='cxc_detail'),
    path('cuentas-pagar/', views.cxp_list, name='cxp_list'),
    path('cuentas-pagar/nueva/', views.cxp_create, name='cxp_create'),
    path('cuentas-pagar/<int:pk>/', views.cxp_detail, name='cxp_detail'),
    path('bancos/', views.banco_list, name='banco_list'),
    path('bancos/nuevo/', views.banco_create, name='banco_create'),
    path('cuentas-bancarias/', views.cuenta_list, name='cuenta_list'),
    path('cuentas-bancarias/nueva/', views.cuenta_create, name='cuenta_create'),
    path('cuentas-bancarias/<int:pk>/', views.cuenta_detail, name='cuenta_detail'),
    path('cajas/', views.caja_list, name='caja_list'),
    path('cajas/nueva/', views.caja_create, name='caja_create'),
    path('cajas/<int:pk>/', views.caja_detail, name='caja_detail'),
    path('movimientos-caja/nuevo/', views.movimiento_caja_create, name='movimiento_caja_create'),
    path('transferencias/', views.transferencia_list, name='transferencia_list'),
    path('transferencias/nueva/', views.transferencia_create, name='transferencia_create'),
    path('flujo-caja/', views.flujo_caja, name='flujo_caja'),
]
from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/reporte-pdf/', views.exportar_clientes_pdf, name='exportar_clientes_pdf'),
    # Productos
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/disponibilidad/', views.disponibilidad_productos, name='disponibilidad'),
    # Pedidos y Cotizaciones
    path('pedidos/', views.pedido_list, name='pedido_list'),
    path('pedidos/nuevo/', views.pedido_create, name='pedido_create'),
    path('cotizaciones/', views.cotizacion_list, name='cotizacion_list'),
    path('cotizaciones/nueva/', views.cotizacion_create, name='cotizacion_create'),
]
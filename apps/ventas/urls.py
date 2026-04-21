from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.dashboard_ventas, name='dashboard'),

    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('clientes/<int:pk>/contacto/nuevo/', views.cliente_contacto_add, name='cliente_contacto_add'),

    # Productos
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/editar/', views.producto_edit, name='producto_edit'),

    # Cotizaciones
    path('cotizaciones/', views.cotizacion_list, name='cotizacion_list'),
    path('cotizaciones/nueva/', views.cotizacion_create, name='cotizacion_create'),
    path('cotizaciones/<int:pk>/', views.cotizacion_detail, name='cotizacion_detail'),
    path('cotizaciones/<int:pk>/enviar/', views.cotizacion_enviar, name='cotizacion_enviar'),
    path('cotizaciones/<int:pk>/aceptar/', views.cotizacion_aceptar, name='cotizacion_aceptar'),
    path('cotizaciones/<int:pk>/convertir/', views.cotizacion_convertir_pedido, name='cotizacion_convertir_pedido'),

    # Pedidos
    path('pedidos/', views.pedido_list, name='pedido_list'),
    path('pedidos/nuevo/', views.pedido_create, name='pedido_create'),
    path('pedidos/<int:pk>/', views.pedido_detail, name='pedido_detail'),
    path('pedidos/<int:pk>/confirmar/', views.pedido_confirmar, name='pedido_confirmar'),

    # Despachos
    path('despachos/', views.despacho_list, name='despacho_list'),
    path('despachos/nuevo/<int:pedido_pk>/', views.despacho_create, name='despacho_create'),
    path('despachos/<int:pk>/', views.despacho_detail, name='despacho_detail'),
]
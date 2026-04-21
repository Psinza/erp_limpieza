from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('', views.dashboard_facturacion, name='dashboard'),
    
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/crear/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    
    # Facturas
    path('facturas/', views.factura_list, name='factura_list'),
    path('facturas/crear/', views.factura_create, name='factura_create'),
    path('facturas/<int:pk>/', views.factura_detail, name='factura_detail'),
    path('facturas/<int:pk>/pdf/', views.factura_pdf, name='factura_pdf'),
    
    # Notas de Entrega
    path('notas-entrega/', views.nota_entrega_list, name='nota_entrega_list'),
    path('notas-entrega/crear/', views.nota_entrega_create, name='nota_entrega_create'),
    
    # Presupuestos
    path('presupuestos/', views.presupuesto_list, name='presupuesto_list'),
    path('presupuestos/crear/', views.presupuesto_create, name='presupuesto_create'),
    path('presupuestos/<int:pk>/', views.presupuesto_detail, name='presupuesto_detail'),
]
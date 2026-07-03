from django.urls import path
from . import views

app_name = 'facturacion'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('facturas/', views.factura_list, name='factura_list'),
    path('facturas/nueva/', views.factura_create, name='factura_create'),
    path('presupuestos/', views.presupuesto_list, name='presupuesto_list'),
    path('presupuestos/nuevo/', views.presupuesto_create, name='presupuesto_create'),
    path('notas-entrega/', views.nota_entrega_list, name='nota_entrega_list'),
    path('notas-entrega/nueva/', views.nota_entrega_create, name='nota_entrega_create'),
    path('libro-ventas/', views.libro_ventas, name='libro_ventas'),
    path('configurar-correlativos/', views.configurar_correlativos, name='configurar_correlativos'),
]
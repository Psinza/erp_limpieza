from django.urls import path
from . import views

app_name = 'compras'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Proveedores
    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/nuevo/', views.proveedor_create, name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', views.proveedor_update, name='proveedor_update'),
    # Materias Primas
    path('materias-primas/', views.materia_prima_list, name='materia_prima_list'),
    path('materias-primas/nueva/', views.materia_prima_create, name='materia_prima_create'),
    path('materias-primas/<int:pk>/editar/', views.materia_prima_update, name='materia_prima_update'),
    # Productos de Compra
    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
]
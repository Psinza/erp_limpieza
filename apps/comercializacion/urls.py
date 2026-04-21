from django.urls import path
from . import views

app_name = 'comercializacion'

urlpatterns = [
    path('', views.dashboard_comercializacion, name='dashboard'),
    
    # Categorías
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/crear/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),
    
    # Información Comercial
    path('productos/', views.producto_comercial_list, name='producto_comercial_list'),
    path('productos/crear/', views.producto_comercial_create, name='producto_comercial_create'),
    path('productos/<int:pk>/editar/', views.producto_comercial_update, name='producto_comercial_update'),
    path('productos/<int:pk>/eliminar/', views.producto_comercial_delete, name='producto_comercial_delete'),
    
    # Listas de Precio
    path('listas/', views.lista_precio_list, name='lista_precio_list'),
    path('listas/crear/', views.lista_precio_create, name='lista_precio_create'),
    path('listas/<int:pk>/editar/', views.lista_precio_update, name='lista_precio_update'),
    path('listas/<int:pk>/eliminar/', views.lista_precio_delete, name='lista_precio_delete'),
    
    # Items de Precio
    path('listas/<int:lista_id>/items/', views.item_precio_list, name='item_precio_list'),
    path('listas/<int:lista_id>/items/crear/', views.item_precio_create, name='item_precio_create'),
    path('items/<int:pk>/editar/', views.item_precio_update, name='item_precio_update'),
    path('items/<int:pk>/eliminar/', views.item_precio_delete, name='item_precio_delete'),
]
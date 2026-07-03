from django.urls import path
from . import views

app_name = 'transportes'

urlpatterns = [
    path('', views.dashboard_transportes, name='dashboard'),
    path('dashboard/', views.dashboard_transportes, name='dashboard_transportes'),
    
    # Vehículos
    path('vehiculos/', views.vehiculo_lista, name='vehiculo_list'),
    path('vehiculos/nuevo/', views.vehiculo_crear, name='vehiculo_create'),
    path('vehiculos/<int:pk>/', views.vehiculo_detalle, name='vehiculo_detail'), # Ya existe
    path('vehiculos/<int:pk>/editar/', views.vehiculo_editar, name='vehiculo_edit'),
    path('vehiculos/<int:pk>/eliminar/', views.vehiculo_eliminar, name='vehiculo_delete'),
    
    # Conductores
    path('conductores/', views.conductor_lista, name='conductor_list'),
    path('conductores/nuevo/', views.conductor_crear, name='conductor_create'),
    path('conductores/<int:pk>/', views.conductor_detalle, name='conductor_detail'), # Ya existe
    path('conductores/<int:pk>/editar/', views.conductor_editar, name='conductor_edit'), # Ya existe
    path('conductores/<int:pk>/eliminar/', views.conductor_eliminar, name='conductor_delete'),
    
    # Despachos
    path('despachos/', views.despacho_lista, name='despacho_list'),
    path('despachos/nuevo/', views.despacho_crear, name='despacho_create'),
    path('despachos/<int:pk>/', views.despacho_detalle, name='despacho_detail'), # Vista existente, URL faltante
    path('despachos/<int:pk>/finalizar/', views.despacho_finalizar, name='despacho_finalizar'), # Vista existente, URL faltante
    path('despachos/<int:pk>/editar/', views.despacho_editar, name='despacho_edit'),
    path('despachos/<int:pk>/eliminar/', views.despacho_eliminar, name='despacho_delete'),

    # Tipo de Vehículo (CRUD)
    path('tipos-vehiculo/', views.tipo_vehiculo_lista, name='tipo_vehiculo_list'),
    path('tipos-vehiculo/nuevo/', views.tipo_vehiculo_crear, name='tipo_vehiculo_create'),
    path('tipos-vehiculo/<int:pk>/editar/', views.tipo_vehiculo_editar, name='tipo_vehiculo_update'),
    path('tipos-vehiculo/<int:pk>/eliminar/', views.tipo_vehiculo_eliminar, name='tipo_vehiculo_delete'),

    # Zonas (CRUD)
    path('zonas/', views.zona_lista, name='zona_list'),
    path('zonas/nuevo/', views.zona_crear, name='zona_create'),
    path('zonas/<int:pk>/editar/', views.zona_editar, name='zona_update'),
    path('zonas/<int:pk>/eliminar/', views.zona_eliminar, name='zona_delete'),

    # Rutas (CRUD)
    path('rutas/', views.ruta_lista, name='ruta_list'),
    path('rutas/nuevo/', views.ruta_crear, name='ruta_create'),
    path('rutas/<int:pk>/', views.ruta_detalle, name='ruta_detail'),
    path('rutas/<int:pk>/editar/', views.ruta_editar, name='ruta_update'),
    path('rutas/<int:pk>/eliminar/', views.ruta_eliminar, name='ruta_delete'),

    # Puntos de Entrega (CRUD - como sub-recursos de Ruta o separados)
    # Se asume que pueden tener vistas propias para crear/editar/eliminar,
    # aunque en la práctica podrían gestionarse como inlines en la edición de Ruta.
    path('rutas/<int:ruta_pk>/puntos/nuevo/', views.punto_entrega_crear, name='punto_entrega_create'),
    path('puntos-entrega/<int:pk>/editar/', views.punto_entrega_editar, name='punto_entrega_update'),
    path('puntos-entrega/<int:pk>/eliminar/', views.punto_entrega_eliminar, name='punto_entrega_delete'),

    # Mantenimientos (CRUD)
    path('mantenimientos/', views.mantenimiento_lista, name='mantenimiento_list'),
    path('mantenimientos/nuevo/', views.mantenimiento_crear, name='mantenimiento_create'),
    path('mantenimientos/<int:pk>/', views.mantenimiento_detalle, name='mantenimiento_detail'),
    path('mantenimientos/<int:pk>/editar/', views.mantenimiento_editar, name='mantenimiento_update'),
    path('mantenimientos/<int:pk>/eliminar/', views.mantenimiento_eliminar, name='mantenimiento_delete'),

    # Entregas de Despacho (CRUD - como sub-recursos de Despacho)
    # Similar a PuntoEntrega, pueden gestionarse como inlines.
    path('despachos/<int:despacho_pk>/entregas/nuevo/', views.entrega_despacho_crear, name='entrega_despacho_create'),
    path('entregas/<int:pk>/editar/', views.entrega_despacho_editar, name='entrega_despacho_update'),
    path('entregas/<int:pk>/eliminar/', views.entrega_despacho_eliminar, name='entrega_despacho_delete'),
]
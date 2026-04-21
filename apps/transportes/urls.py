from django.urls import path
from . import views

app_name = 'transportes'

urlpatterns = [
    path('', views.dashboard_transportes, name='dashboard'),
    
    # Vehículos
    path('vehiculos/', views.vehiculo_lista, name='vehiculo_list'),
    path('vehiculos/nuevo/', views.vehiculo_crear, name='vehiculo_create'),
    path('vehiculos/<int:pk>/', views.vehiculo_detalle, name='vehiculo_detail'),
    
    # Conductores
    path('conductores/', views.conductor_lista, name='conductor_list'),
    path('conductores/nuevo/', views.conductor_crear, name='conductor_create'),
    path('conductores/<int:pk>/', views.conductor_detalle, name='conductor_detail'),
    path('conductores/<int:pk>/editar/', views.conductor_editar, name='conductor_edit'),
    
    # Despachos
    path('despachos/', views.despacho_lista, name='despacho_list'),
    path('despachos/nuevo/', views.despacho_crear, name='despacho_create'),
]
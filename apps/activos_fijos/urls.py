from django.urls import path
from . import views

app_name = 'activos_fijos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('lista/', views.activo_list, name='activo_list'),
    path('nuevo/', views.activo_create, name='activo_create'),
    path('<int:pk>/', views.activo_detail, name='activo_detail'),
    path('<int:pk>/editar/', views.activo_edit, name='activo_edit'),
    path('<int:pk>/eliminar/', views.activo_delete, name='activo_delete'),
    path('reporte-depreciacion/', views.reporte_depreciacion, name='reporte_depreciacion'),
    path('<int:pk>/asignacion/', views.asignacion_create, name='asignacion_create'),
    path('<int:pk>/mantenimiento/', views.mantenimiento_create, name='mantenimiento_create'),
]
from django.urls import path
from . import views

app_name = 'activos_fijos'

urlpatterns = [
    path('', views.ActivoFijoListView.as_view(), name='activo_list'), # Lista y búsqueda
    path('nuevo/', views.ActivoFijoCreateView.as_view(), name='activo_create'),
    path('editar/<int:pk>/', views.ActivoFijoUpdateView.as_view(), name='activo_update'),
    path('eliminar/<int:pk>/', views.ActivoFijoDeleteView.as_view(), name='activo_delete'),
    path('exportar/', views.exportar_activos_a_excel, name='exportar_excel'), # Exportar a Excel
    path('reporte-depreciacion/', views.reporte_depreciacion, name='reporte_depreciacion'),
]
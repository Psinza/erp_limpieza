from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mantenimiento/', views.mantenimiento, name='mantenimiento'),
    path('respaldos/', views.lista_respaldos, name='lista_respaldos'),
    path('ejecutar-backup/', views.ejecutar_backup, name='ejecutar_backup'),
    path('ejecutar-backup-manual/', views.ejecutar_backup, name='ejecutar_backup_manual'),
    path('download-logs/', views.download_logs, name='download_logs'),
    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/toggle/<int:pk>/', views.usuario_toggle, name='usuario_toggle'),
    path('usuarios/roles/<int:pk>/', views.usuario_roles, name='usuario_roles'),
    path('usuarios/eliminar/<int:pk>/', views.usuario_delete, name='usuario_delete'),
    path('roles/', views.rol_list, name='rol_list'),
]
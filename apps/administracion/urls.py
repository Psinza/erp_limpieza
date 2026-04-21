from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('mantenimiento/', views.mantenimiento_sistema, name='mantenimiento'),
    path('configuracion/', views.configuracion_empresa, name='configuracion'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/nuevo/', views.editar_usuario, name='nuevo_usuario'),
]
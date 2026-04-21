from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación
    path('login/',           views.login_view,       name='login'),
    path('logout/',          views.logout_view,       name='logout'),

    # Dashboard
    path('dashboard/',       views.dashboard,         name='dashboard'),

    # Perfil
    path('perfil/',          views.perfil,            name='perfil'),
    path('perfil/password/', views.cambiar_password,  name='cambiar_password'),

    # Usuarios
    path('usuarios/',             views.usuario_lista,  name='usuario_lista'),
    path('usuarios/nuevo/',       views.usuario_crear,  name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/toggle/', views.usuario_toggle, name='usuario_toggle'),

    # Roles
    path('roles/',                views.rol_lista,    name='rol_lista'),
    path('roles/nuevo/',          views.rol_crear,    name='rol_crear'),
    path('roles/<int:pk>/editar/',views.rol_editar,   name='rol_editar'),
]

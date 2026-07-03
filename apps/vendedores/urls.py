from django.urls import path
from . import views

app_name = 'vendedores'

urlpatterns = [
    path('', views.dashboard_vendedores, name='dashboard'),
    path('lista/', views.vendedor_list, name='vendedor_list'),
    path('nuevo/', views.vendedor_create, name='vendedor_create'),
    path('<int:pk>/editar/', views.vendedor_edit, name='vendedor_edit'),
    path('comisiones/', views.comision_list, name='comision_list'),
    path('comisiones/nueva/', views.comision_create, name='comision_create'),
]
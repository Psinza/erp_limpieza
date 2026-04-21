from django.urls import path
from . import views

app_name = 'viaticos'

urlpatterns = [
    path('', views.dashboard_viaticos, name='dashboard'),
    path('solicitudes/', views.solicitud_list, name='solicitud_list'),
    path('solicitudes/crear/', views.solicitud_create, name='solicitud_create'),
    path('solicitudes/<int:pk>/', views.solicitud_detail, name='solicitud_detail'),
    path('solicitudes/<int:pk>/aprobar/', views.solicitud_aprobar, name='solicitud_aprobar'),
    path('solicitudes/<int:solicitud_pk>/gastos/crear/', views.gasto_create, name='gasto_create'),
]
from django.urls import path
from . import views

app_name = 'viaticos'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('nuevo/', views.solicitud_create, name='solicitud_create'),
    path('editar/<int:pk>/', views.solicitud_update, name='solicitud_update'),
    path('eliminar/<int:pk>/', views.solicitud_delete, name='solicitud_delete'),
]
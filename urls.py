from django.urls import path
from . import views

app_name = 'vendedores'

urlpatterns = [
    path('dashboard/', views.dashboard_vendedores, name='dashboard'),
    path('comisiones/', views.comisiones_list, name='comisiones_list'),
    path('metas/', views.metas_form, name='metas_form'),
]
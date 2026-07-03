from django.urls import path
from . import views

app_name = 'produccion'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Rutas adicionales (vistas pendientes de implementar)
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/nueva/', views.orden_create, name='orden_create'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    path('materias-primas/', views.materia_prima_list, name='materia_prima_list'),
    path('formulas/', views.formula_list, name='formula_list'),
    path('formulas/nueva/', views.formula_create, name='formula_create'),
    path('formulas/<int:pk>/', views.formula_detail, name='formula_detail'),
    path('formulas/<int:pk>/editar/', views.formula_update, name='formula_update'),
    path('productos-terminados/', views.producto_terminado_list, name='producto_terminado_list'),
    path('productos-terminados/nuevo/', views.producto_terminado_create, name='producto_terminado_create'),
]
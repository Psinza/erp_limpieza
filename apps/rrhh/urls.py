from django.urls import path
from . import views

app_name = 'rrhh'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Empleados
    path('empleados/', views.empleado_list, name='empleado_list'),
    path('empleados/nuevo/', views.empleado_create, name='empleado_create'),
    path('empleados/<int:pk>/', views.empleado_detail, name='empleado_detail'),
    path('empleados/<int:pk>/editar/', views.empleado_update, name='empleado_edit'),
    path('empleados/<int:pk>/eliminar/', views.empleado_delete, name='empleado_delete'),
    
    # Nóminas
    path('nominas/', views.nomina_list, name='nomina_list'),
    path('nominas/dashboard/', views.nomina_list, name='dashboard_nominas'),
    path('nominas/nueva/', views.nomina_create, name='nomina_create'),
    path('nominas/crear/', views.nomina_create, name='crear_nomina'),
    path('nominas/<int:pk>/', views.nomina_detail, name='nomina_detail'),
    path('nominas/<int:pk>/detalle/', views.nomina_detail, name='detalle_nomina'),
    path('nominas/<int:pk>/calcular/', views.nomina_calcular, name='nomina_calcular'),
    path('nominas/<int:pk>/aprobar/', views.nomina_aprobar, name='nomina_aprobar'),
    path('nominas/<int:pk>/pagar/', views.nomina_pagar, name='nomina_pagar'),
    path('nominas/<int:pk>/agregar-empleado/', views.nomina_agregar_empleado, name='nomina_agregar_empleado'),
    path('nominas/recibo/<int:pk>/pdf/', views.recibo_pdf, name='recibo_pdf'),
    
    # Vacaciones
    path('vacaciones/', views.vacacion_list, name='vacacion_list'),
    path('vacaciones/nueva/', views.vacacion_create, name='vacacion_create'),
    
    # Estructura
    path('departamentos/', views.departamento_list, name='departamento_list'),
    path('departamentos/nuevo/', views.departamento_create, name='departamento_create'),
    path('departamentos/<int:pk>/editar/', views.departamento_update, name='departamento_edit'),
    path('cargos/', views.cargo_list, name='cargo_list'),
    path('cargos/nuevo/', views.cargo_create, name='cargo_create'),
]
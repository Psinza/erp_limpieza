# apps/rrhh/urls.py
from django.urls import path
from . import views

app_name = "rrhh"

urlpatterns = [
    path("",                   views.dashboard_rrhh,      name="dashboard"),
    path("departamentos/",     views.departamento_list,    name="departamento_list"),
    path("departamentos/nuevo/",views.departamento_create,  name="departamento_create"),
    path("empleados/",         views.empleado_list,        name="empleado_list"),
    path("empleados/nuevo/",    views.empleado_create,      name="empleado_create"),
    
    # Nóminas
    path("nominas/",           views.nomina_list,          name="nomina_list"),
    path("nominas/nueva/",      views.nomina_create,        name="nomina_create"),
    
    # Vacaciones
    path("vacaciones/",        views.vacacion_list,        name="vacacion_list"),
    path("vacaciones/nueva/",   views.vacacion_create,      name="vacacion_create"),
]

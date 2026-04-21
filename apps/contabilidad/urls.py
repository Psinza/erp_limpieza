# apps/contabilidad/urls.py
from django.urls import path
from . import views

app_name = "contabilidad"

urlpatterns = [
    # Dashboard
    path("",                                              views.dashboard_contabilidad,    name="dashboard"),

    # Ejercicios contables
    path("ejercicios/",                                   views.ejercicio_list,            name="ejercicio_list"),
    path("ejercicios/nuevo/",                             views.ejercicio_create,          name="ejercicio_create"),
    path("ejercicios/<int:pk>/cerrar/",                   views.ejercicio_cerrar,          name="ejercicio_cerrar"),

    # Plan de cuentas
    path("plan-cuentas/",                                 views.plan_cuentas,              name="plan_cuentas"),
    path("plan-cuentas/nueva/",                           views.cuenta_create,             name="cuenta_create"),
    path("plan-cuentas/<int:pk>/editar/",                 views.cuenta_edit,               name="cuenta_edit"),
    path("plan-cuentas/<int:pk>/mayor/",                  views.cuenta_mayor,              name="cuenta_mayor"),

    # Asientos contables
    path("asientos/",                                     views.asiento_list,              name="asiento_list"),
    path("asientos/nuevo/",                               views.asiento_create,            name="asiento_create"),
    path("asientos/<int:pk>/",                            views.asiento_detail,            name="asiento_detail"),
    path("asientos/<int:pk>/agregar-linea/",              views.asiento_agregar_linea,     name="asiento_agregar_linea"),
    path("asientos/<int:pk>/linea/<int:lpk>/eliminar/",   views.asiento_eliminar_linea,    name="asiento_eliminar_linea"),
    path("asientos/<int:pk>/aprobar/",                    views.asiento_aprobar,           name="asiento_aprobar"),
    path("asientos/<int:pk>/anular/",                     views.asiento_anular,            name="asiento_anular"),

    # Reportes
    path("libro-diario/",                                 views.libro_diario,              name="libro_diario"),
    path("balance-comprobacion/",                         views.balance_comprobacion,      name="balance_comprobacion"),
    path("estado-resultados/",                            views.estado_resultados,         name="estado_resultados"),
    path("balance-general/",                              views.balance_general,           name="balance_general"),

    # Configuración contable
    path("configuracion/",                                views.configuracion_list,        name="configuracion_list"),
    path("configuracion/nueva/",                          views.configuracion_create,      name="configuracion_create"),
    path("configuracion/<int:pk>/editar/",                views.configuracion_edit,        name="configuracion_edit"),
]

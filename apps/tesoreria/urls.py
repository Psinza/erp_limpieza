# apps/tesoreria/urls.py
from django.urls import path
from . import views
from apps.core.views import modulo_en_construccion

app_name = "tesoreria"

urlpatterns = [
    # Ejemplo: Redirigiendo el dashboard a la vista genérica con parámetros
    path("", modulo_en_construccion, {'nombre_modulo': 'Tesorería'}, name="dashboard"),
    
    # Bancos y Cuentas
    path("bancos/",    views.banco_list,         name="banco_list"),
    path("bancos/nuevo/", views.banco_create,    name="banco_create"),

    path("cuentas/",   views.cuenta_list,        name="cuenta_list"),
    path("cuentas/nuevo/", views.cuenta_create,  name="cuenta_create"),
    
    # Movimientos
    path("movimientos/bancos/", views.movimiento_banco_list, name="movimiento_banco_list"),
    path("movimientos/bancos/nuevo/", views.movimiento_banco_create, name="movimiento_banco_create"),
    
    # Cajas
    path("cajas/",     views.caja_list,          name="caja_list"),
    path("cajas/nuevo/", views.caja_create,      name="caja_create"),
    path("cajas/<int:caja_id>/movimiento/", views.caja_movimiento_create, name="caja_movimiento_create"),

    
    # CxC y CxP
    path("cxc/",       views.cxc_list,           name="cxc_list"),
    path("cxc/nuevo/", views.cxc_create,         name="cxc_create"),
    path("cxp/",       views.cxp_list,           name="cxp_list"),
    path("cxp/nuevo/", views.cxp_create,         name="cxp_create"),
    
    # Transferencias
    path("transferencias/nuevo/", views.transferencia_create, name="transferencia_create"),
    
    # Reportes
    path("flujo-caja/", views.flujo_caja,        name="flujo_caja"),
]

# apps/produccion/urls.py
from django.urls import path
from . import views

app_name = "produccion"

urlpatterns = [
    path("",                     views.dashboard_produccion,      name="dashboard"),
    path("materias-primas/",     views.materia_prima_list,         name="materia_prima_list"),
    path("productos-terminados/", views.producto_terminado_list,    name="producto_terminado_list"),
    
    path("formulas/",            views.formula_list,               name="formula_list"),
    path("formulas/nueva/",      views.formula_create,             name="formula_create"),
    
    path("ordenes/",             views.orden_list,                 name="orden_list"),
    path("ordenes/nueva/",       views.orden_create,               name="orden_create"),
    
    path("alertas-stock/",       views.alerta_stock_list,          name="alerta_stock_list"),
    path("lotes-qc/",            views.lotes_qc_list,              name="lotes_qc_list"),
    path("lotes/<int:lote_pk>/control-calidad/", views.control_calidad_create, name="control_calidad_create"),
    path("lotes/<int:pk>/liberar/", views.lote_liberar, name="lote_liberar"),
]

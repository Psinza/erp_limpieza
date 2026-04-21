# apps/contabilidad/admin.py
from django.contrib import admin
from .models import (
    EjercicioContable, CuentaContable,
    AsientoContable, LineaAsiento,
    PeriodoContable, ConfiguracionContable,
)


@admin.register(EjercicioContable)
class EjercicioContableAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "año", "fecha_inicio", "fecha_fin", "estado"]
    list_filter   = ["estado"]


@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display  = ["codigo", "nombre", "tipo", "naturaleza", "nivel",
                     "saldo_actual", "acepta_movimientos", "activa"]
    list_filter   = ["tipo", "naturaleza", "nivel", "activa"]
    search_fields = ["codigo", "nombre"]
    readonly_fields = ["saldo_actual"]


class LineaAsientoInline(admin.TabularInline):
    model  = LineaAsiento
    extra  = 2
    fields = ["cuenta", "tipo", "monto", "descripcion"]


@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display    = ["numero", "fecha", "ejercicio", "tipo", "concepto",
                       "total_debe", "total_haber", "estado"]
    list_filter     = ["estado", "tipo", "ejercicio"]
    search_fields   = ["numero", "concepto", "referencia"]
    readonly_fields = ["numero", "total_debe", "total_haber", "creado_en", "modificado_en"]
    inlines         = [LineaAsientoInline]


@admin.register(PeriodoContable)
class PeriodoContableAdmin(admin.ModelAdmin):
    list_display = ["nombre", "ejercicio", "mes", "fecha_inicio", "fecha_fin", "estado"]
    list_filter  = ["estado", "ejercicio"]


@admin.register(ConfiguracionContable)
class ConfiguracionContableAdmin(admin.ModelAdmin):
    list_display  = ["clave", "descripcion", "cuenta"]
    search_fields = ["clave", "descripcion"]

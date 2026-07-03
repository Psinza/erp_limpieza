# apps/produccion/admin.py
from django.contrib import admin
from .models import (
    CategoriaProductoTerminado, CategoriaMateriaPrima,
    ProductoTerminado, MateriaPrima,
    Formula, LineaFormula,
    OrdenProduccion, ControlCalidad
)

@admin.register(CategoriaProductoTerminado)
class CatPTAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]

@admin.register(CategoriaMateriaPrima)
class CatMPAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]

@admin.register(ProductoTerminado)
class ProductoTerminadoAdmin(admin.ModelAdmin):
    list_display  = ["sku", "nombre", "presentacion", "categoria", "stock_actual", "activo"]
    list_filter   = ["presentacion", "categoria", "activo"]
    search_fields = ["sku", "nombre", "registro_sanitario"]

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display  = ["sku", "nombre", "concentracion", "categoria", "stock_actual", "activo"]
    list_filter   = ["categoria", "activo"]
    search_fields = ["sku", "nombre"]

class LineaFormulaInline(admin.TabularInline):
    model  = LineaFormula
    extra  = 1

@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display    = ["codigo", "nombre", "producto", "version", "estado"]
    list_filter     = ["estado", "producto__categoria"]
    inlines         = [LineaFormulaInline]
    search_fields   = ["codigo", "nombre"]

class ControlCalidadInline(admin.StackedInline):
    model = ControlCalidad
    extra = 0

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display    = ["id", "lote_numero", "formula", "cantidad_a_producir", "estado", "prioridad"]
    list_filter     = ["estado", "prioridad", "fecha_planificada"]
    search_fields   = ["lote_numero", "formula__nombre"]
    inlines         = [ControlCalidadInline]

@admin.register(ControlCalidad)
class ControlCalidadAdmin(admin.ModelAdmin):
    list_display = ["orden", "fecha_inspeccion", "aprobado", "inspector", "cumple_covenin"]
    list_filter  = ["aprobado", "cumple_covenin", "fecha_inspeccion"]

# apps/produccion/admin.py
from django.contrib import admin
from .models import (
    CategoriaProductoTerminado, CategoriaMateriaPrima,
    ProductoTerminado, MateriaPrima,
    Formula, LineaFormula,
    OrdenProduccion, LoteProduccion,
)

@admin.register(CategoriaProductoTerminado)
class CatPTAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]

@admin.register(CategoriaMateriaPrima)
class CatMPAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]

@admin.register(ProductoTerminado)
class ProductoTerminadoAdmin(admin.ModelAdmin):
    list_display  = ["sku", "nombre", "categoria", "stock_actual", "activo"]
    search_fields = ["sku", "nombre"]

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display  = ["sku", "nombre", "categoria", "stock_actual", "activo"]
    search_fields = ["sku", "nombre"]

class LineaFormulaInline(admin.TabularInline):
    model  = LineaFormula
    extra  = 1

@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display    = ["nombre", "producto", "version", "esta_activa"]
    inlines         = [LineaFormulaInline]

class LoteInline(admin.TabularInline):
    model  = LoteProduccion
    extra  = 0

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display    = ["id", "formula", "cantidad_a_producir", "estado", "prioridad"]
    inlines         = [LoteInline]

@admin.register(LoteProduccion)
class LoteProduccionAdmin(admin.ModelAdmin):
    list_display = ["numero_lote", "orden", "estado"]

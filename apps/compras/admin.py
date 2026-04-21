# apps/compras/admin.py
from django.contrib import admin
from .models import (
    CategoriaProveedor, Proveedor,
    OrdenCompra,
)

@admin.register(CategoriaProveedor)
class CategoriaProveedorAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]
    search_fields = ["nombre"]

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display   = ["ruc", "razon_social", "categoria", "telefono", "estado", "creado_en"]
    list_filter    = ["estado", "tipo", "categoria"]
    search_fields  = ["ruc", "razon_social", "nombre_comercial"]
    readonly_fields= ["creado_en"]

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display    = ["id", "proveedor", "fecha_emision", "estado", "total"]
    list_filter     = ["estado"]
    search_fields   = ["proveedor__razon_social"]

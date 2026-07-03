from django.contrib import admin

from .models import Proveedor, RetencionISLR, RetencionIVA


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['rif', 'razon_social']
    search_fields = ['rif', 'razon_social']


@admin.register(RetencionIVA)
class RetencionIVAAdmin(admin.ModelAdmin):
    list_display = ['nro_comprobante', 'proveedor', 'nro_factura', 'nro_control', 'monto_iva', 'monto_retenido', 'periodo_fiscal']
    list_filter = ['anulada', 'periodo_fiscal', 'fecha_emision']
    search_fields = ['nro_comprobante', 'proveedor__rif', 'proveedor__razon_social', 'nro_factura', 'nro_control']
    readonly_fields = ['monto_retenido']


@admin.register(RetencionISLR)
class RetencionISLRAdmin(admin.ModelAdmin):
    list_display = ['nro_comprobante', 'proveedor', 'nro_factura', 'codigo_concepto', 'monto_operacion', 'monto_retenido', 'periodo_fiscal']
    list_filter = ['periodo_fiscal', 'fecha_emision']
    search_fields = ['nro_comprobante', 'proveedor__rif', 'proveedor__razon_social', 'nro_factura']
    readonly_fields = ['monto_retenido']

from django.contrib import admin
from .models import SolicitudViatico, GastoViatico

@admin.register(SolicitudViatico)
class SolicitudViaticoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'destino', 'fecha_viaje', 'monto_estimado', 'moneda', 'tasa_bcv', 'estado']
    list_filter = ['estado', 'moneda', 'fecha_viaje', 'fecha_solicitud']
    search_fields = ['empleado__nombre', 'destino', 'motivo']

@admin.register(GastoViatico)
class GastoViaticoAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'tipo', 'descripcion', 'fecha', 'monto', 'moneda', 'nro_factura', 'nro_control', 'es_reembolsable']
    list_filter = ['tipo', 'moneda', 'es_reembolsable', 'fecha']
    search_fields = ['descripcion', 'proveedor_rif', 'proveedor_nombre', 'nro_factura', 'nro_control', 'solicitud__empleado__nombre']

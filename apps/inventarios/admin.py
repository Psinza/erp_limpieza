from django.contrib import admin

from .models import GuiaDespacho, MovimientoInventario


@admin.register(GuiaDespacho)
class GuiaDespachoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'razon_social_receptor', 'destino', 'transportista_nombre', 'estado', 'fecha_emision')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('numero', 'numero_control', 'rif_receptor', 'razon_social_receptor', 'vehiculo_placa')
    readonly_fields = ('fecha_emision',)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'motivo', 'cantidad', 'documento_tipo', 'documento_numero', 'usuario', 'fecha')
    list_filter = ('tipo', 'motivo', 'documento_tipo', 'producto')
    search_fields = ('documento_numero', 'numero_control', 'referencia', 'lote', 'producto__nombre', 'producto__codigo')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)

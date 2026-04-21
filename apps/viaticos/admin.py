from django.contrib import admin
from .models import SolicitudViatico, GastoViatico

@admin.register(SolicitudViatico)
class SolicitudViaticoAdmin(admin.ModelAdmin):
    list_display = ['solicitante', 'destino', 'fecha_inicio', 'fecha_fin', 'monto_solicitado', 'estado']
    list_filter = ['estado', 'fecha_inicio', 'fecha_creacion']
    search_fields = ['solicitante__username', 'destino', 'motivo']

@admin.register(GastoViatico)
class GastoViaticoAdmin(admin.ModelAdmin):
    list_display = ['solicitud', 'tipo', 'descripcion', 'fecha', 'monto']
    list_filter = ['tipo', 'fecha']
    search_fields = ['descripcion', 'solicitud__solicitante__username']
from django.contrib import admin
from .models import SolicitudPago


@admin.register(SolicitudPago)
class SolicitudPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'monto', 'estado', 'autorizado_por', 'fecha_solicitud')
    list_filter = ('estado',)
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha_solicitud'
    readonly_fields = ('fecha_solicitud',)

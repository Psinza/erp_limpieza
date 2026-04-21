# apps/transportes/admin.py
from django.contrib import admin
from .models import (
    TipoVehiculo, Vehiculo, Conductor,
    Zona, Ruta, PuntoEntrega,
    Despacho, EntregaDespacho, Mantenimiento,
)


@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display  = ["nombre"]
    search_fields = ["nombre"]


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display  = ["placa", "marca", "modelo", "año", "tipo",
                     "estado", "odometro", "soat_vencimiento"]
    list_filter   = ["estado", "tipo", "combustible"]
    search_fields = ["placa", "marca", "modelo"]
    readonly_fields = ["creado_en", "modificado_en"]


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display  = ["cedula", "apellidos", "nombres", "categoria_licencia",
                     "licencia_vencimiento", "estado", "vehiculo_asignado"]
    list_filter   = ["estado", "categoria_licencia"]
    search_fields = ["cedula", "nombres", "apellidos"]
    readonly_fields = ["creado_en", "modificado_en"]


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "activa"]
    search_fields = ["nombre"]


class PuntoEntregaInline(admin.TabularInline):
    model  = PuntoEntrega
    extra  = 1
    fields = ["orden", "nombre", "direccion", "cliente_ref", "tiempo_estimado", "activo"]


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "zona", "origen", "destino",
                    "distancia_km", "tiempo_estimado", "estado"]
    list_filter  = ["zona", "estado"]
    search_fields= ["codigo", "nombre"]
    inlines      = [PuntoEntregaInline]


class EntregaDespachoInline(admin.TabularInline):
    model  = EntregaDespacho
    extra  = 0
    fields = ["punto_entrega", "hora_llegada", "estado", "firma_receptor"]


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display    = ["numero", "ruta", "vehiculo", "conductor",
                       "fecha_salida", "estado", "km_recorridos"]
    list_filter     = ["estado"]
    search_fields   = ["numero", "vehiculo__placa", "conductor__apellidos"]
    readonly_fields = ["numero", "km_recorridos", "creado_en", "modificado_en"]
    inlines         = [EntregaDespachoInline]


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ["vehiculo", "tipo", "descripcion",
                    "fecha_programada", "estado", "costo"]
    list_filter  = ["estado", "tipo"]
    search_fields= ["vehiculo__placa", "descripcion"]

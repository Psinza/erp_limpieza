from django.contrib import admin
from .models import ActivoFijo

@admin.register(ActivoFijo)
class ActivoFijoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'fecha_adquisicion', 'valor_compra', 'estado')
    search_fields = ('codigo', 'nombre')
    list_filter = ('estado',)
from django.contrib import admin

from .models import ActivoFijo


@admin.register(ActivoFijo)
class ActivoFijoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'fecha_adquisicion', 'valor_compra', 'nro_factura', 'nro_control', 'estado')
    search_fields = ('codigo', 'nombre', 'nro_factura', 'nro_control', 'proveedor_rif')
    list_filter = ('estado',)

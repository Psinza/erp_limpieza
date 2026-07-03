from django.contrib import admin
from .models import Vendedor, Comision


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'usuario', 'codigo_empleado', 'comision_porcentaje', 'meta_mensual', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'cedula', 'codigo_empleado', 'usuario__username', 'usuario__first_name')
    list_editable = ('activo',)


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'pedido_venta', 'monto_venta', 'porcentaje_aplicado', 'monto_comision', 'retencion_islr', 'fecha_calculo', 'pagado')
    list_filter = ('pagado', 'vendedor')
    list_editable = ('pagado',)
    date_hierarchy = 'fecha_calculo'

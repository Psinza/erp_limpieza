from django.contrib import admin
from .models import Cliente, Factura, ItemFactura, NotaEntrega, Presupuesto, ItemPresupuesto

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ruc', 'email', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'ruc', 'email']

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha_emision', 'total', 'estado']
    list_filter = ['estado', 'fecha_emision']
    search_fields = ['numero', 'cliente__nombre']

@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ['factura', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['descripcion', 'factura__numero']

@admin.register(NotaEntrega)
class NotaEntregaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha']
    list_filter = ['fecha']
    search_fields = ['numero', 'cliente__nombre']

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha_emision', 'total', 'estado']
    list_filter = ['estado', 'fecha_emision']
    search_fields = ['numero', 'cliente__nombre']

@admin.register(ItemPresupuesto)
class ItemPresupuestoAdmin(admin.ModelAdmin):
    list_display = ['presupuesto', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['descripcion', 'presupuesto__numero']
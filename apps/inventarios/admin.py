from django.contrib import admin
from .models import MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'referencia', 'usuario', 'fecha')
    list_filter = ('tipo', 'producto')
    search_fields = ('referencia', 'producto__nombre')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)

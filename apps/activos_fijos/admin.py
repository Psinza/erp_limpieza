from django.contrib import admin
from .models import ActivoFijo

@admin.register(ActivoFijo)
class ActivoFijoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'fecha_adquisicion', 'valor_compra', 'estado']
    search_fields = ['codigo', 'nombre']
    list_filter = ['categoria', 'estado', 'fecha_adquisicion']
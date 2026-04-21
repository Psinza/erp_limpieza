from django.contrib import admin
from .models import Departamento, Empleado

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombres', 'apellidos', 'departamento', 'cargo', 'activo')
    list_filter = ('departamento', 'activo')
    search_fields = ('cedula', 'nombres', 'apellidos')

from django.contrib import admin
from .models import EjercicioContable, CuentaContable, AsientoContable, LineaAsiento, PeriodoContable, ConfiguracionContable

@admin.register(EjercicioContable)
class EjercicioContableAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'cerrado')
    list_filter = ('cerrado',)
    search_fields = ('nombre',)

class LineaAsientoInline(admin.TabularInline):
    model = LineaAsiento
    extra = 1
    fields = ('cuenta', 'debe', 'haber', 'descripcion')

@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'descripcion', 'ejercicio', 'estado', 'creado_por', 'fecha_creacion')
    list_filter = ('estado', 'ejercicio', 'fecha')
    search_fields = ('numero', 'descripcion', 'creado_por__username')
    inlines = [LineaAsientoInline]
    readonly_fields = ('numero', 'fecha_creacion', 'fecha_aprobacion')

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Only set creado_por on creation
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'naturaleza', 'padre', 'saldo_actual', 'activo')
    list_filter = ('tipo', 'naturaleza', 'activo', 'es_cuenta_mayor')
    search_fields = ('codigo', 'nombre')
    raw_id_fields = ('padre',) # For better UX with many accounts

@admin.register(PeriodoContable)
class PeriodoContableAdmin(admin.ModelAdmin):
    list_display = ('ejercicio', 'mes', 'anio', 'fecha_inicio', 'fecha_fin', 'cerrado')
    list_filter = ('ejercicio', 'cerrado')
    search_fields = ('ejercicio__nombre',)

@admin.register(ConfiguracionContable)
class ConfiguracionContableAdmin(admin.ModelAdmin):
    list_display = ('clave', 'cuenta', 'descripcion')
    search_fields = ('clave', 'cuenta__nombre')
    raw_id_fields = ('cuenta',)
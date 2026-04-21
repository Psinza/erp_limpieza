from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, Area, Permiso, LogAcceso


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nombre', 'activo')
    list_filter   = ('activo',)
    search_fields = ('nombre', 'codigo')


class PermisoInline(admin.TabularInline):
    model  = Permiso
    extra  = 2
    fields = ('area', 'accion')


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display    = ('nombre', 'nivel', 'activo', 'creado')
    list_filter     = ('nivel', 'activo')
    search_fields   = ('nombre',)
    filter_horizontal = ('areas',)
    inlines         = [PermisoInline]


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display  = ('username', 'nombre_completo', 'area', 'rol', 'estado', 'activo', 'ultimo_acceso')
    list_filter   = ('estado', 'activo', 'area', 'rol')
    search_fields = ('username', 'nombres', 'apellidos', 'cedula', 'email')
    ordering      = ('apellidos',)

    fieldsets = (
        ('Acceso', {'fields': ('username', 'password')}),
        ('Datos personales', {'fields': ('nombres', 'apellidos', 'cedula', 'telefono', 'email', 'foto')}),
        ('Organización', {'fields': ('area', 'rol', 'cargo')}),
        ('Estado', {'fields': ('estado', 'activo', 'is_staff', 'is_superuser')}),
        ('Auditoría', {'fields': ('ultimo_acceso', 'intentos_fallidos'), 'classes': ('collapse',)}),
        ('Permisos Django', {'fields': ('groups', 'user_permissions'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nombres', 'apellidos',
                       'area', 'rol', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('ultimo_acceso', 'intentos_fallidos')


@admin.register(LogAcceso)
class LogAccesoAdmin(admin.ModelAdmin):
    list_display  = ('username', 'tipo', 'ip', 'timestamp')
    list_filter   = ('tipo', 'timestamp')
    search_fields = ('username', 'ip')
    readonly_fields = ('usuario', 'username', 'tipo', 'ip', 'user_agent', 'timestamp', 'detalle')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

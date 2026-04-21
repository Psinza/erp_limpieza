from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


# ─── ÁREAS DEL SISTEMA ───────────────────────────────────────────────────────

class Area(models.Model):
    AREAS = [
        ('RRHH',        'Recursos Humanos'),
        ('ADMIN',       'Administración'),
        ('COMPRAS',     'Compras'),
        ('VENTAS',      'Ventas'),
        ('TESORERIA',   'Tesorería'),
        ('ORD_PAGOS',   'Ordenación de Pagos'),
        ('CONTAB',      'Contabilidad'),
        ('PRODUCCION',  'Producción'),
        ('COMERCIAL',   'Comercialización'),
        ('LOGISTICA',   'Logística'),
        ('ALMACEN_MP',  'Almacén Materias Primas'),
        ('ALMACEN_PT',  'Almacén Productos Terminados'),
        ('TRANSPORTE',  'Transportes'),
        ('VENDEDORES',  'Vendedores'),
    ]

    codigo   = models.CharField(max_length=20, choices=AREAS, unique=True)
    nombre   = models.CharField(max_length=100)
    activo   = models.BooleanField(default=True)
    creado   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ─── ROLES ───────────────────────────────────────────────────────────────────

class Rol(models.Model):
    NIVELES = [
        ('SOLO_LECTURA',  'Solo Lectura'),
        ('LECTURA_ESCRITURA', 'Lectura y Escritura'),
        ('APROBADOR',     'Aprobador'),
        ('SUPERVISOR',    'Supervisor'),
        ('SUPERUSUARIO',  'Superusuario'),
    ]

    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    nivel       = models.CharField(max_length=20, choices=NIVELES, default='LECTURA_ESCRITURA')
    areas       = models.ManyToManyField(Area, related_name='roles', blank=True)
    activo      = models.BooleanField(default=True)
    creado      = models.DateTimeField(auto_now_add=True)
    modificado  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_display()})"


# ─── PERMISOS GRANULARES ──────────────────────────────────────────────────────

class Permiso(models.Model):
    ACCIONES = [
        ('ver',      'Ver'),
        ('crear',    'Crear'),
        ('editar',   'Editar'),
        ('eliminar', 'Eliminar'),
        ('aprobar',  'Aprobar'),
        ('exportar', 'Exportar'),
        ('reportar', 'Generar Reportes'),
    ]

    rol     = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos')
    area    = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='permisos')
    accion  = models.CharField(max_length=20, choices=ACCIONES)

    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        unique_together = ('rol', 'area', 'accion')

    def __str__(self):
        return f"{self.rol.nombre} → {self.area.nombre} → {self.get_accion_display()}"


# ─── USUARIO PERSONALIZADO ────────────────────────────────────────────────────

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ESTADOS = [
        ('ACTIVO',    'Activo'),
        ('INACTIVO',  'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('VACACIONES','Vacaciones'),
    ]

    # Datos de acceso
    username    = models.CharField('Usuario', max_length=50, unique=True)
    email       = models.EmailField('Correo', unique=True)

    # Datos personales
    nombres     = models.CharField('Nombres', max_length=100)
    apellidos   = models.CharField('Apellidos', max_length=100)
    cedula      = models.CharField('Cédula', max_length=20, unique=True, blank=True, null=True)
    telefono    = models.CharField('Teléfono', max_length=20, blank=True)
    foto        = models.ImageField('Foto', upload_to='usuarios/', blank=True, null=True)

    # Relaciones organizativas
    area        = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='usuarios', verbose_name='Área')
    rol         = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='usuarios', verbose_name='Rol')
    cargo       = models.CharField('Cargo', max_length=100, blank=True)

    # Estado y control
    estado      = models.CharField('Estado', max_length=20, choices=ESTADOS, default='ACTIVO')
    activo      = models.BooleanField('Activo', default=True)
    is_staff    = models.BooleanField('Staff', default=False)

    # Auditoría
    fecha_creacion      = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion  = models.DateTimeField('Última modificación', auto_now=True)
    ultimo_acceso       = models.DateTimeField('Último acceso', null=True, blank=True)
    intentos_fallidos   = models.PositiveSmallIntegerField('Intentos fallidos', default=0)

    objects = UsuarioManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'nombres', 'apellidos']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.username})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def tiene_permiso(self, area_codigo, accion):
        """Verifica si el usuario tiene un permiso específico."""
        if self.is_superuser:
            return True
        if not self.rol or not self.activo:
            return False
        return Permiso.objects.filter(
            rol=self.rol,
            area__codigo=area_codigo,
            accion=accion
        ).exists()

    def puede_ver(self, area_codigo):
        return self.tiene_permiso(area_codigo, 'ver')

    def puede_crear(self, area_codigo):
        return self.tiene_permiso(area_codigo, 'crear')

    def puede_editar(self, area_codigo):
        return self.tiene_permiso(area_codigo, 'editar')

    def puede_eliminar(self, area_codigo):
        return self.tiene_permiso(area_codigo, 'eliminar')

    def puede_aprobar(self, area_codigo):
        return self.tiene_permiso(area_codigo, 'aprobar')

    def registrar_acceso(self):
        self.ultimo_acceso = timezone.now()
        self.intentos_fallidos = 0
        self.save(update_fields=['ultimo_acceso', 'intentos_fallidos'])

    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.estado = 'BLOQUEADO'
        self.save(update_fields=['intentos_fallidos', 'estado'])


# ─── SESIÓN / AUDITORÍA DE ACCESOS ───────────────────────────────────────────

class LogAcceso(models.Model):
    TIPOS = [
        ('LOGIN',   'Inicio de sesión'),
        ('LOGOUT',  'Cierre de sesión'),
        ('FALLIDO', 'Intento fallido'),
        ('BLOQUEO', 'Cuenta bloqueada'),
    ]

    usuario     = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True,
                                     related_name='logs_acceso')
    username    = models.CharField(max_length=50)  # por si el usuario es eliminado
    tipo        = models.CharField(max_length=10, choices=TIPOS)
    ip          = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    detalle     = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Log de Acceso'
        verbose_name_plural = 'Logs de Acceso'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.username} — {self.get_tipo_display()} — {self.timestamp:%d/%m/%Y %H:%M}"

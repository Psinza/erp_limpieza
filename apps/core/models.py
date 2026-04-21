from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

class EjercicioContable(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ejercicio Contable"
        verbose_name_plural = "Ejercicios Contables"

class CuentaContable(models.Model):
    TIPOS_CUENTA = (
        ('activo', 'Activo'),
        ('pasivo', 'Pasivo'),
        ('patrimonio', 'Patrimonio'),
        ('ingreso', 'Ingreso'),
        ('costo', 'Costo'),
        ('egreso', 'Egreso'),
    )
    NATURALEZA_CUENTA = (
        ('deudora', 'Deudora'),
        ('acreedora', 'Acreedora'),
    )

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPOS_CUENTA)
    naturaleza = models.CharField(max_length=20, choices=NATURALEZA_CUENTA)
    padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='hijos')
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    saldo_actual = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    es_cuenta_mayor = models.BooleanField(default=False, help_text="Indica si es una cuenta de mayor (no permite asientos directos)")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def clean(self):
        if self.padre and self.padre.es_cuenta_mayor and not self.padre.hijos.exists():
            # Allow a major account to be a parent if it doesn't have children yet
            pass
        elif self.padre and not self.padre.es_cuenta_mayor:
            raise ValidationError("Una cuenta solo puede tener como padre una cuenta de mayor.")

        # Logic to determine if it's a major account based on having children
        # This should be handled before saving, or in a pre_save signal
        # For simplicity, we'll assume if it has children, it's a major account
        # and if it doesn't, it's a detail account.
        # This field might be better as a property or managed by a signal.
        pass # The actual logic for es_cuenta_mayor will be handled in save()

    def save(self, *args, **kwargs):
        # Update es_cuenta_mayor based on whether it has children
        # This needs to be done carefully to avoid recursion or integrity issues
        # For now, we'll set it based on if it's intended to be a parent.
        # A more robust solution might involve a post_save signal or a separate management command.
        # For the purpose of forms, we'll keep it simple.
        if self.pk: # If updating an existing account
            if self.hijos.exists():
                self.es_cuenta_mayor = True
            else:
                self.es_cuenta_mayor = False
        else: # If creating a new account, assume it's a detail account unless specified
            self.es_cuenta_mayor = False # Default for new accounts

        self.full_clean() # Call clean method before saving
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        ordering = ['codigo']

class AsientoContable(models.Model):
    ESTADOS_ASIENTO = (
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('anulado', 'Anulado'),
    )
    numero = models.CharField(max_length=50, unique=True, blank=True)
    fecha = models.DateField()
    descripcion = models.TextField()
    ejercicio = models.ForeignKey(EjercicioContable, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADOS_ASIENTO, default='borrador')
    creado_por = models.ForeignKey('erp_core_app.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Asiento N° {self.numero} - {self.fecha}"

    def balanceado(self):
        debe = self.lineas.aggregate(Sum('debe'))['debe__sum'] or 0
        haber = self.lineas.aggregate(Sum('haber'))['haber__sum'] or 0
        return debe == haber and self.lineas.exists()

    def save(self, *args, **kwargs):
        if not self.numero:
            # Generate a sequential number for the asiento
            last_asiento = AsientoContable.objects.filter(ejercicio=self.ejercicio).order_by('-fecha_creacion').first()
            if last_asiento and last_asiento.numero: # Ensure last_asiento.numero is not None
                try:
                    last_num = int(last_asiento.numero.split('-')[-1])
                    self.numero = f"{self.ejercicio.nombre}-{last_num + 1:05d}"
                except (ValueError, IndexError):
                    self.numero = f"{self.ejercicio.nombre}-00001" # Fallback if parsing fails
            else:
                self.numero = f"{self.ejercicio.nombre}-00001"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        ordering = ['-fecha', '-numero']

class LineaAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='lineas')
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
    debe = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    haber = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Línea {self.id} - {self.cuenta.nombre}: Debe {self.debe}, Haber {self.haber}"

    def clean(self):
        if self.cuenta.es_cuenta_mayor:
            raise ValidationError("No se pueden registrar movimientos directamente en una cuenta de mayor. Seleccione una cuenta de detalle.")
        if self.debe > 0 and self.haber > 0:
            raise ValidationError("Una línea de asiento no puede tener valores en Debe y Haber simultáneamente.")
        if self.debe == 0 and self.haber == 0:
            raise ValidationError("Una línea de asiento debe tener un valor en Debe o Haber.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Update account balance only if the asiento is approved
        if self.asiento.estado == 'aprobado':
            if self.cuenta.naturaleza == 'deudora':
                self.cuenta.saldo_actual += self.debe - self.haber
            else: # acreedora
                self.cuenta.saldo_actual += self.haber - self.debe
            self.cuenta.save(update_fields=['saldo_actual'])

    class Meta:
        verbose_name = "Línea de Asiento"
        verbose_name_plural = "Líneas de Asiento"

class PeriodoContable(models.Model):
    ejercicio = models.ForeignKey(EjercicioContable, on_delete=models.CASCADE, related_name='periodos')
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveSmallIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ejercicio', 'mes', 'anio')
        verbose_name = "Período Contable"
        verbose_name_plural = "Períodos Contables"
        ordering = ['anio', 'mes']

    def __str__(self):
        return f"{self.mes}/{self.anio} ({self.ejercicio.nombre})"

class ConfiguracionContable(models.Model):
    clave = models.CharField(max_length=100, unique=True, help_text="Clave para identificar la configuración (ej. 'cuenta_ventas')")
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT, help_text="Cuenta contable asociada a esta clave")
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.clave}: {self.cuenta.nombre}"

    class Meta:
        verbose_name = "Configuración Contable"
        verbose_name_plural = "Configuraciones Contables"


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

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='usuario_set',
        related_query_name='usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',
        related_query_name='usuario',
    )

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
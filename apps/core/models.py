from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


rif_validator = RegexValidator(
    regex=r'^[JGVEP]-?\d{7,9}-?\d?$',
    message='Use RIF venezolano. Ej: J-12345678-9.',
)


class Area(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    nivel = models.CharField(max_length=20, default='LECTURA_ESCRITURA')
    areas = models.ManyToManyField(Area, blank=True, related_name='roles')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    username = models.CharField(max_length=50, unique=True, verbose_name='Usuario')
    email = models.EmailField(unique=True, verbose_name='Correo')
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Cedula')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono')
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True, verbose_name='Foto')
    cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    estado = models.CharField(max_length=20, default='ACTIVO')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return self.get_full_name() or self.username


class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    rif = models.CharField(max_length=20, unique=True, validators=[rif_validator])
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='empresa/', null=True, blank=True)
    contador_nombre = models.CharField(max_length=150, blank=True)
    contador_cpc = models.CharField(max_length=50, blank=True)
    contador_rif = models.CharField(max_length=20, blank=True, validators=[rif_validator])
    gerente_nombre = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.nombre


class EjercicioContable(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class PeriodoContable(models.Model):
    ejercicio = models.ForeignKey(EjercicioContable, on_delete=models.CASCADE, related_name='periodos')
    mes = models.PositiveSmallIntegerField()
    anio = models.PositiveSmallIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ejercicio', 'mes', 'anio')

    def __str__(self):
        return f'{self.mes:02d}/{self.anio}'


class CuentaContable(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20)
    naturaleza = models.CharField(max_length=20)
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    saldo_actual = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    es_cuenta_mayor = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='hijos')

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class ConfiguracionContable(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)

    def __str__(self):
        return self.clave


class AsientoContable(models.Model):
    numero = models.CharField(max_length=50, unique=True, blank=True)
    fecha = models.DateField()
    descripcion = models.TextField()
    ejercicio = models.ForeignKey(EjercicioContable, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, default='borrador')
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.numero or f'Asiento {self.pk}'


class LineaAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='lineas')
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
    debe = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    haber = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.cuenta} D:{self.debe} H:{self.haber}'


class Proveedor(models.Model):
    razon_social = models.CharField(max_length=255)
    rif = models.CharField(max_length=20, unique=True, validators=[rif_validator])
    direccion = models.TextField()

    def __str__(self):
        return f"{self.rif} - {self.razon_social}"


class RetencionIVA(models.Model):
    nro_comprobante = models.CharField(max_length=14, unique=True, help_text="Formato: AAAAMMDDDDDDDD")
    fecha_emision = models.DateField(default=timezone.now)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='retenciones_iva')
    nro_factura = models.CharField(max_length=50)
    nro_control = models.CharField(max_length=50)
    fecha_factura = models.DateField()
    tipo_transaccion = models.CharField(max_length=2, default='01')
    monto_total_compra = models.DecimalField(max_digits=15, decimal_places=2)
    base_imponible = models.DecimalField(max_digits=15, decimal_places=2)
    monto_iva = models.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_retencion = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('75.00'))
    monto_retenido = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    periodo_fiscal = models.CharField(max_length=6, blank=True)
    anulada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.monto_retenido = self.monto_iva * (self.porcentaje_retencion / Decimal('100.00'))
        if not self.periodo_fiscal:
            self.periodo_fiscal = self.fecha_emision.strftime("%Y%m")
        super().save(*args, **kwargs)

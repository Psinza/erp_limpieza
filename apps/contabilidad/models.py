from django.db import models
from django.utils import timezone
from decimal import Decimal

class CuentaContable(models.Model):
    TIPO_CUENTA = [
        ('A', 'Activo'),
        ('P', 'Pasivo'),
        ('C', 'Capital / Patrimonio'),
        ('I', 'Ingreso'),
        ('E', 'Egreso / Gasto'),
    ]

    codigo = models.CharField(max_length=50, unique=True, help_text="Código de la cuenta según VEN-NIF")
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=1, choices=TIPO_CUENTA)
    cuenta_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcuentas')
    permite_movimientos = models.BooleanField(default=True, help_text="False si es una cuenta agrupadora")
    
    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class EjercicioFiscal(models.Model):
    anio = models.IntegerField(unique=True, verbose_name="Año Fiscal")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Ejercicio Fiscal"
        verbose_name_plural = "Ejercicios Fiscales"
        ordering = ['-anio']

    def __str__(self):
        return f"Ejercicio {self.anio}"

class ComprobanteDiario(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('asentado', 'Asentado'),
        ('anulado', 'Anulado')
    ]
    numero = models.CharField(max_length=20, unique=True)
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField()
    ejercicio_fiscal = models.ForeignKey(EjercicioFiscal, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comprobante de Diario"
        verbose_name_plural = "Comprobantes de Diario"
        ordering = ['-fecha', '-numero']

    def __str__(self):
        return f"CD-{self.numero} - {self.fecha}"

class LineaComprobante(models.Model):
    comprobante = models.ForeignKey(ComprobanteDiario, on_delete=models.CASCADE, related_name='lineas')
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=255, blank=True)
    debe = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    haber = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Línea de Comprobante"
        verbose_name_plural = "Líneas de Comprobantes"

    def __str__(self):
        return f"{self.comprobante.numero} - {self.cuenta.codigo} D:{self.debe} H:{self.haber}"
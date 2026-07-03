from datetime import date
from decimal import Decimal

from django.core.validators import RegexValidator
from django.db import models


rif_validator = RegexValidator(
    regex=r'^[JGVEP]-?\d{7,9}-?\d?$',
    message='Use RIF venezolano. Ej: J-12345678-9.',
)


class ActivoFijo(models.Model):
    ESTADO_CHOICES = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('retirado', 'Retirado'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_adquisicion = models.DateField()
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2)
    nro_factura = models.CharField(max_length=50, blank=True, verbose_name='Nro. factura')
    nro_control = models.CharField(max_length=50, blank=True, verbose_name='Nro. control fiscal')
    proveedor_rif = models.CharField(max_length=20, blank=True, validators=[rif_validator])
    vida_util_meses = models.IntegerField(help_text='Vida util en meses')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='operativo')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def depreciacion_mensual(self):
        if self.vida_util_meses > 0:
            return self.valor_compra / Decimal(self.vida_util_meses)
        return Decimal('0.00')

    @property
    def valor_actual(self):
        hoy = date.today()
        meses_pasados = (hoy.year - self.fecha_adquisicion.year) * 12 + hoy.month - self.fecha_adquisicion.month
        if meses_pasados <= 0:
            return self.valor_compra
        if meses_pasados >= self.vida_util_meses:
            return Decimal('0.00')
        return self.valor_compra - (self.depreciacion_mensual * Decimal(meses_pasados))

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal

cedula_validator = RegexValidator(
    regex=r'^[VE]-?\d{6,9}$',
    message="Use cedula venezolana o extranjera. Ej: V-12345678.",
)

class Vendedor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendedor',
    )
    codigo_empleado = models.CharField(max_length=30, unique=True, blank=True)
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True, validators=[cedula_validator])
    comision_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    meta_mensual = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class Comision(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    pedido_venta = models.ForeignKey('ventas.Pedido', on_delete=models.SET_NULL, null=True, blank=True, related_name='comisiones')
    monto_venta = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    monto_comision = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    fecha = models.DateField(null=True, blank=True)
    fecha_calculo = models.DateField(auto_now_add=True)
    porcentaje_aplicado = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    base_imponible = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    retencion_islr = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    referencia_pago = models.CharField(max_length=80, blank=True)
    pagado = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Comisiones"

    def clean(self):
        super().clean()
        if self.monto_comision > self.monto_venta and self.monto_venta > 0:
            raise ValidationError({'monto_comision': 'La comision no puede superar el monto base de venta.'})

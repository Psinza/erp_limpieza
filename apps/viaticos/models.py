from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal

rif_validator = RegexValidator(
    regex=r'^[JGVEP]-?\d{7,9}-?\d?$',
    message="Use RIF venezolano. Ej: J-12345678-9.",
)

class SolicitudViatico(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('rendido', 'Rendido'),
    ]
    
    empleado = models.ForeignKey('rrhh.Empleado', on_delete=models.CASCADE, related_name='viaticos', null=True, blank=True, help_text="Seleccione si es un empleado registrado")
    beneficiario_nombre = models.CharField(max_length=200, blank=True, verbose_name="Nombre del Beneficiario")
    beneficiario_cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    beneficiario_departamento = models.CharField(max_length=100, blank=True, verbose_name="Departamento")
    
    fecha_solicitud = models.DateField(auto_now_add=True, null=True, blank=True)
    fecha_viaje = models.DateField()
    destino = models.CharField(max_length=200)
    motivo = models.TextField()
    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    moneda = models.CharField(max_length=3, choices=[('VES', 'Bolivares'), ('USD', 'Dolares')], default='VES')
    tasa_bcv = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('1.0000'))
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Solicitud {self.id} - {self.empleado} a {self.destino}"

class GastoViatico(models.Model):
    TIPOS_GASTO = [
        ('transporte', 'Transporte'),
        ('alojamiento', 'Alojamiento'),
        ('alimentacion', 'Alimentación'),
        ('otros', 'Otros'),
    ]
    solicitud = models.ForeignKey(SolicitudViatico, on_delete=models.CASCADE, related_name='gastos')
    tipo = models.CharField(max_length=20, choices=TIPOS_GASTO)
    descripcion = models.CharField(max_length=200)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=[('VES', 'Bolivares'), ('USD', 'Dolares')], default='VES')
    tasa_bcv = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('1.0000'))
    proveedor_rif = models.CharField(max_length=20, blank=True, validators=[rif_validator])
    proveedor_nombre = models.CharField(max_length=200, blank=True)
    nro_factura = models.CharField(max_length=50, blank=True, verbose_name='Nro. factura')
    nro_control = models.CharField(max_length=50, blank=True, verbose_name='Nro. control')
    es_reembolsable = models.BooleanField(default=True)
    comprobante = models.FileField(upload_to='comprobantes_viaticos/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.monto}"

    @property
    def monto_ves(self):
        if self.moneda == 'USD':
            return self.monto * self.tasa_bcv
        return self.monto

    def clean(self):
        super().clean()
        if self.es_reembolsable:
            faltantes = {}
            if not self.proveedor_rif:
                faltantes['proveedor_rif'] = 'Requerido para soportar el gasto fiscalmente.'
            if not self.nro_factura:
                faltantes['nro_factura'] = 'Requerido para soportar el gasto fiscalmente.'
            if not self.nro_control:
                faltantes['nro_control'] = 'Requerido para soportar el gasto fiscalmente.'
            if not self.comprobante:
                faltantes['comprobante'] = 'Adjunte factura, recibo o soporte digital.'
            if faltantes:
                raise ValidationError(faltantes)
        if self.monto <= 0:
            raise ValidationError({'monto': 'El monto debe ser mayor que cero.'})

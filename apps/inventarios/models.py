from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.compras.models import ProductoCompra


rif_validator = RegexValidator(
    regex=r'^[JGVEP]-\d{8}-\d$',
    message='Use el formato RIF venezolano: J-12345678-9.',
)

cedula_validator = RegexValidator(
    regex=r'^[VE]-\d{6,9}$',
    message='Use el formato de cedula: V-12345678 o E-12345678.',
)


class GuiaDespacho(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('emitida', 'Emitida'),
        ('anulada', 'Anulada'),
    ]

    numero = models.CharField(max_length=30, unique=True, verbose_name='Nro. guia de despacho')
    numero_control = models.CharField(max_length=30, blank=True, verbose_name='Nro. de control')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')

    rif_emisor = models.CharField(max_length=12, validators=[rif_validator])
    razon_social_emisor = models.CharField(max_length=200)
    rif_receptor = models.CharField(max_length=12, validators=[rif_validator])
    razon_social_receptor = models.CharField(max_length=200)

    origen = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    transportista_nombre = models.CharField(max_length=200)
    transportista_rif = models.CharField(max_length=12, validators=[rif_validator], blank=True)
    vehiculo_placa = models.CharField(max_length=20)
    conductor_nombre = models.CharField(max_length=150)
    conductor_cedula = models.CharField(max_length=12, validators=[cedula_validator])
    licencia_grado = models.CharField(max_length=30, blank=True)
    tipo_carga = models.CharField(max_length=120)
    peso_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unidad_peso = models.CharField(max_length=20, default='kg')
    clase_embalaje = models.CharField(max_length=120, blank=True)
    sin_derecho_credito_fiscal = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Guia de despacho'
        verbose_name_plural = 'Guias de despacho'
        ordering = ['-fecha_emision']

    def clean(self):
        if not self.sin_derecho_credito_fiscal:
            raise ValidationError({
                'sin_derecho_credito_fiscal': 'Las guias de despacho deben indicar que no dan derecho a credito fiscal.'
            })

    def __str__(self):
        return f"Guia {self.numero} - {self.razon_social_receptor}"


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]

    MOTIVO_CHOICES = [
        ('compra', 'Recepcion de compra'),
        ('venta', 'Despacho por venta'),
        ('traslado_guia', 'Traslado con guia de despacho'),
        ('devolucion', 'Devolucion'),
        ('consumo', 'Consumo interno o produccion'),
        ('merma', 'Merma o deterioro'),
        ('ajuste_fiscal', 'Ajuste documentado'),
    ]

    DOCUMENTO_CHOICES = [
        ('FACTURA', 'Factura'),
        ('GUIA_DESPACHO', 'Guia de despacho'),
        ('NOTA_ENTREGA', 'Nota de entrega'),
        ('ACTA_AJUSTE', 'Acta de ajuste'),
        ('ORDEN_PRODUCCION', 'Orden de produccion'),
    ]

    producto = models.ForeignKey(ProductoCompra, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES, default='ajuste_fiscal')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    fecha = models.DateTimeField(auto_now_add=True)

    documento_tipo = models.CharField(max_length=20, choices=DOCUMENTO_CHOICES, default='ACTA_AJUSTE')
    documento_numero = models.CharField(max_length=100, help_text='Ej: FAC-000123, GD-000045 o REC-2026-0001')
    numero_control = models.CharField(max_length=30, blank=True, verbose_name='Nro. de control fiscal')
    guia_despacho = models.ForeignKey(GuiaDespacho, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos')
    referencia = models.CharField(max_length=100, blank=True, help_text='Referencia interna del ERP')

    lote = models.CharField(max_length=60, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    origen = models.CharField(max_length=255, blank=True)
    destino = models.CharField(max_length=255, blank=True)
    costo_unitario = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    tasa_bcv = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('1.0000'), verbose_name='Tasa BCV')
    observaciones = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_inventarios',
    )

    class Meta:
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['producto', 'fecha']),
            models.Index(fields=['documento_tipo', 'documento_numero']),
            models.Index(fields=['lote']),
        ]

    def clean(self):
        if self.motivo == 'traslado_guia' and not self.guia_despacho:
            raise ValidationError({'guia_despacho': 'Los traslados deben estar amparados por guia de despacho.'})
        if self.documento_tipo == 'FACTURA' and not self.numero_control:
            raise ValidationError({'numero_control': 'Las facturas deben conservar el numero de control fiscal.'})

    @property
    def valor_total(self):
        return self.cantidad * self.costo_unitario

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"

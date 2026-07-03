from django.db import models
from django.utils import timezone
from decimal import Decimal
from apps.ventas.models import Cliente, Pedido, ProductoVenta
from .models_correlativos import CorrelativoFiscal

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=255)
    rif = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.rif} - {self.razon_social}"

class RetencionIVA(models.Model):
    """
    Modelo de Retención de IVA según Providencia Administrativa SNAT/2015/0049.
    """
    nro_comprobante = models.CharField(max_length=14, unique=True, help_text="Formato: AAAAMMDDDDDDDD")
    fecha_emision = models.DateField(default=timezone.now)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='retenciones_iva')
    
    # Datos del documento afectado (Factura de Compra)
    nro_factura = models.CharField(max_length=50)
    nro_control = models.CharField(max_length=50)
    fecha_factura = models.DateField()
    tipo_transaccion = models.CharField(max_length=2, default='01', help_text="01-Registro, 02-Nota Debito, 03-Nota Credito")
    
    # Montos Fiscales
    monto_total_compra = models.DecimalField(max_digits=15, decimal_places=2)
    base_imponible = models.DecimalField(max_digits=15, decimal_places=2)
    monto_iva = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Lógica de Retención
    porcentaje_retencion = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('75.00'))
    monto_retenido = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    
    periodo_fiscal = models.CharField(max_length=6, help_text="Formato: AAAAMM")
    anulada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # El monto retenido es el IVA por el porcentaje de retención
        self.monto_retenido = self.monto_iva * (self.porcentaje_retencion / Decimal('100.00'))
        
        # Generación automática del periodo fiscal si no existe
        if not self.periodo_fiscal:
            self.periodo_fiscal = self.fecha_emision.strftime("%Y%m")
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Retención de IVA"
        verbose_name_plural = "Retenciones de IVA"
        ordering = ['-fecha_emision', '-nro_comprobante']

class RetencionISLR(models.Model):
    """
    Modelo de Retención de ISLR según Decreto 1808 (Venezuela).
    """
    nro_comprobante = models.CharField(max_length=20, unique=True, verbose_name="Número de Comprobante")
    fecha_emision = models.DateField(default=timezone.now, verbose_name="Fecha de Emisión")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='retenciones_islr')
    
    # Documento afectado
    nro_factura = models.CharField(max_length=50, verbose_name="Número de Factura")
    fecha_factura = models.DateField(verbose_name="Fecha de Factura")
    
    # Datos del cálculo
    codigo_concepto = models.CharField(max_length=10, help_text="Ej: 001 para Honorarios Profesionales")
    monto_operacion = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Base Imponible")
    porcentaje_retencion = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% Retención")
    sustraendo = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), help_text="Monto en Bs. a restar del cálculo")
    
    monto_retenido = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    periodo_fiscal = models.CharField(max_length=6, help_text="AAAAMM")

    def save(self, *args, **kwargs):
        # Cálculo legal: (Base * %) - Sustraendo
        monto_bruto = self.monto_operacion * (self.porcentaje_retencion / Decimal('100.00'))
        self.monto_retenido = max(Decimal('0.00'), monto_bruto - self.sustraendo)
        
        if not self.periodo_fiscal:
            self.periodo_fiscal = self.fecha_emision.strftime("%Y%m")
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ISLR {self.nro_comprobante} - {self.proveedor.razon_social}"

    class Meta:
        verbose_name = "Retención de ISLR"
        verbose_name_plural = "Retenciones de ISLR"
        ordering = ['-fecha_emision']

class FacturaVenta(models.Model):
    TIPO_CHOICES = [
        ('factura', 'Factura'),
        ('nota_debito', 'Nota de Débito'),
        ('nota_credito', 'Nota de Crédito'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, related_name='facturas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas')
    
    tipo_documento = models.CharField(max_length=20, choices=TIPO_CHOICES, default='factura')
    numero_factura = models.CharField(max_length=50, unique=True)
    numero_control = models.CharField(max_length=50, unique=True, help_text="Número de control fiscal")
    
    fecha_emision = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
    # Desglose de impuestos (SENIAT)
    exento = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    base_imponible = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    base_imponible_reducida = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    base_imponible_suntuaria = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    iva_general_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("16.00"))
    iva_reducida_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("8.00"))
    iva_suntuaria_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("31.00"))
    
    monto_iva_general = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    monto_iva_reducida = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    monto_iva_suntuaria = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    igtf_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("3.00"))
    monto_igtf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"), help_text="Impuesto a Grandes Transacciones Financieras")
    
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    anulada = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Factura de Venta"
        verbose_name_plural = "Facturas de Venta"
        ordering = ['-fecha_emision', '-numero_factura']

    def __str__(self):
        return f"{self.get_tipo_documento_display()} {self.numero_factura} - {self.cliente.razon_social}"

    def calcular_totales(self):
        detalles = self.detalles.all()
        self.exento = sum(d.cantidad * d.precio_unitario for d in detalles if d.tipo_impuesto == 'exento')
        self.base_imponible = sum(d.cantidad * d.precio_unitario for d in detalles if d.tipo_impuesto == 'general')
        self.base_imponible_reducida = sum(d.cantidad * d.precio_unitario for d in detalles if d.tipo_impuesto == 'reducida')
        self.base_imponible_suntuaria = sum(d.cantidad * d.precio_unitario for d in detalles if d.tipo_impuesto == 'suntuaria')
        
        self.monto_iva_general = self.base_imponible * (self.iva_general_pct / Decimal('100'))
        self.monto_iva_reducida = self.base_imponible_reducida * (self.iva_reducida_pct / Decimal('100'))
        self.monto_iva_suntuaria = self.base_imponible_suntuaria * (self.iva_suntuaria_pct / Decimal('100'))
        
        # Subtotal antes de IGTF
        subtotal_con_iva = (
            self.exento + 
            self.base_imponible + self.monto_iva_general +
            self.base_imponible_reducida + self.monto_iva_reducida +
            self.base_imponible_suntuaria + self.monto_iva_suntuaria
        )
        
        # IGTF se calcula sobre el total si aplica (en este caso lo dejamos como campo editable o base de calculo)
        # Generalmente es el 3% del total pagado en divisas.
        self.total = subtotal_con_iva + self.monto_igtf
        self.save()

class DetalleFacturaVenta(models.Model):
    factura = models.ForeignKey(FacturaVenta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(ProductoVenta, on_delete=models.PROTECT)
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=15, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2)
    
    # 0=Exento, 16=General, 8=Reducida, 31=Suntuaria
    tipo_impuesto = models.CharField(max_length=20, choices=[('exento', 'Exento'), ('general', 'General (16%)'), ('reducida', 'Reducida (8%)'), ('suntuaria', 'Suntuaria (31%)')], default='general')
    monto_impuesto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Facturas"

    def save(self, *args, **kwargs):
        base = self.cantidad * self.precio_unitario
        if self.tipo_impuesto == 'general':
            self.monto_impuesto = base * Decimal('0.16')
        elif self.tipo_impuesto == 'reducida':
            self.monto_impuesto = base * Decimal('0.08')
        elif self.tipo_impuesto == 'suntuaria':
            self.monto_impuesto = base * Decimal('0.31')
        else:
            self.monto_impuesto = Decimal('0.00')
            
        self.subtotal = base + self.monto_impuesto
        super().save(*args, **kwargs)
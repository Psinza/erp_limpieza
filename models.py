from django.db import models
from django.utils import timezone
from decimal import Decimal

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=255)
    rif = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    
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
    nro_control = models.CharField(max_length=50, verbose_name="Número de Control", default="0")
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
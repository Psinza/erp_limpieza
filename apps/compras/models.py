from django.conf import settings
from django.db import models
from decimal import Decimal
from django.utils import timezone
from apps.facturacion.models import Proveedor
# Asumiendo que existe un modelo Producto en apps.inventarios o logistica, o usaremos un string por ahora
# from apps.inventarios.models import Producto

class ProductoCompra(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio_referencia = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.nombre

class OrdenCompra(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_emision = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=[('borrador', 'Borrador'), ('aprobada', 'Aprobada'), ('recibida', 'Recibida')], default='borrador')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"OC-{self.numero}"

class FacturaCompra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='facturas_compra')
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True, related_name='facturas')
    
    numero_factura = models.CharField(max_length=50)
    numero_control = models.CharField(max_length=50, help_text="Número de control fiscal")
    fecha_emision = models.DateField()
    fecha_recepcion = models.DateField(default=timezone.now)
    
    # Desglose de impuestos
    exento = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    base_imponible = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    base_imponible_reducida = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    base_imponible_suntuaria = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    monto_iva_general = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    monto_iva_reducida = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    monto_iva_suntuaria = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    igtf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    
    estado = models.CharField(max_length=20, choices=[('registrada', 'Registrada'), ('pagada', 'Pagada'), ('anulada', 'Anulada')], default='registrada')
    registrada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Factura de Compra"
        verbose_name_plural = "Facturas de Compra"
        unique_together = ('proveedor', 'numero_factura')

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.proveedor.razon_social}"

class DetalleFacturaCompra(models.Model):
    factura = models.ForeignKey(FacturaCompra, on_delete=models.CASCADE, related_name='detalles')
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=15, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2)
    tipo_impuesto = models.CharField(max_length=20, choices=[('exento', 'Exento'), ('general', 'General (16%)'), ('reducida', 'Reducida (8%)'), ('suntuaria', 'Suntuaria (31%)')], default='general')
    monto_impuesto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)

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

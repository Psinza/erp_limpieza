from django.db import models
from apps.produccion.models import ProductoTerminado, MateriaPrima

class Almacen(models.Model):
    """Define las bodegas del sistema (Materia Prima, Productos Terminados, etc.)"""
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255, blank=True)
    es_principal = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, choices=[
        ('MP', 'Materia Prima'),
        ('PT', 'Producto Terminado'),
        ('MIXTO', 'Mixto')
    ], default='MIXTO')

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"

class MovimientoInventario(models.Model):
    """Representa el Kardex de movimientos detallados para control de inventario."""
    TIPOS = (
        ('E', 'Entrada'), 
        ('S', 'Salida'), 
        ('T', 'Transferencia')
    )
    
    tipo = models.CharField(max_length=1, choices=TIPOS)
    almacen_origen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='salidas', null=True, blank=True)
    almacen_destino = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='entradas', null=True, blank=True)
    
    producto_pt = models.ForeignKey(ProductoTerminado, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Producto Terminado")
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Materia Prima")
    
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Costo al momento del movimiento")
    saldo_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Stock acumulado en el almacén después de este registro")
    
    fecha = models.DateTimeField(auto_now_add=True)
    documento_referencia = models.CharField(max_length=100, blank=True, help_text="Factura, Orden de Producción o Guía de Remisión")
    motivo = models.CharField(max_length=255, blank=True)

    def __str__(self):
        item = self.materia_prima.nombre if self.materia_prima else self.producto_pt.nombre
        return f"{self.get_tipo_display()} | {item} | Cant: {self.cantidad}"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Kardex de Inventario"
        ordering = ['-fecha']
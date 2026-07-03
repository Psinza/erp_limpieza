from django.conf import settings
from django.db import models

class Almacen(models.Model):
    """Representa un lugar físico de almacenamiento (Materia Prima, Producto Terminado, etc.)"""
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255, blank=True)
    es_principal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Almacenes"

class ExistenciaAlmacen(models.Model):
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='existencias')
    materia_prima = models.ForeignKey('produccion.MateriaPrima', on_delete=models.CASCADE, null=True, blank=True)
    producto_pt = models.ForeignKey('produccion.ProductoTerminado', on_delete=models.CASCADE, null=True, blank=True)
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = (('almacen', 'materia_prima'), ('almacen', 'producto_pt'))

    def __str__(self):
        item = self.materia_prima.nombre if self.materia_prima else (self.producto_pt.nombre if self.producto_pt else "Desconocido")
        return f"{self.almacen.nombre} - {item}: {self.stock}"

class MovimientoInventario(models.Model):
    """Historial de entradas y salidas de stock."""
    TIPO_MOVIMIENTO = [
        ('E', 'Entrada'),
        ('S', 'Salida'),
        ('T', 'Transferencia'),
    ]
    
    MOTIVOS = [
        ('compra', 'Recepción de Compra'),
        ('produccion', 'Producción de Lote'),
        ('consumo', 'Consumo en Producción'),
        ('venta', 'Despacho de Venta'),
        ('ajuste', 'Ajuste de Inventario'),
        ('transferencia', 'Transferencia entre Almacenes'),
    ]
    materia_prima = models.ForeignKey('produccion.MateriaPrima', on_delete=models.CASCADE, related_name='movimientos', null=True, blank=True)
    producto_pt = models.ForeignKey('produccion.ProductoTerminado', on_delete=models.CASCADE, related_name='movimientos', null=True, blank=True)
    tipo = models.CharField(max_length=1, choices=TIPO_MOVIMIENTO)
    motivo = models.CharField(max_length=20, choices=MOTIVOS, default='ajuste')
    almacen_origen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='salidas', null=True, blank=True)
    almacen_destino = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='entradas', null=True, blank=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_stock = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_logistica')
    referencia = models.CharField(max_length=100, null=True, blank=True, help_text="Ej: Consumo OP-123, Compra OC-45")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Procesar Stock
            item_field = 'materia_prima' if self.materia_prima else 'producto_pt'
            item_val = self.materia_prima if self.materia_prima else self.producto_pt
            
            # Salida (Origen)
            if self.tipo in ['S', 'T'] and self.almacen_origen:
                exist, _ = ExistenciaAlmacen.objects.get_or_create(
                    almacen=self.almacen_origen,
                    **{item_field: item_val}
                )
                exist.stock -= self.cantidad
                exist.save()
            
            # Entrada (Destino)
            if self.tipo in ['E', 'T'] and self.almacen_destino:
                exist, _ = ExistenciaAlmacen.objects.get_or_create(
                    almacen=self.almacen_destino,
                    **{item_field: item_val}
                )
                exist.stock += self.cantidad
                exist.save()
            
            # Actualizar stock maestro en el modelo de producción
            if item_val:
                item_val.stock_actual = ExistenciaAlmacen.objects.filter(**{item_field: item_val}).aggregate(total=models.Sum('stock'))['total'] or 0
                item_val.save()

    def __str__(self):
        item = self.materia_prima.nombre if self.materia_prima else (self.producto_pt.nombre if self.producto_pt else "Desconocido")
        return f"{self.get_tipo_display()} - {item} ({self.cantidad})"

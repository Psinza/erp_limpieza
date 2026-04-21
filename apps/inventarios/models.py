from django.db import models
from apps.produccion.models import MateriaPrima
from django.contrib.auth import get_user_model

User = get_user_model()

class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada (Compra/Ajuste)'),
        ('SALIDA', 'Salida (Venta/Consumo)'),
    ]
    
    producto = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    
    referencia = models.CharField(max_length=100, help_text="Ej: REC-2025-0001")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"
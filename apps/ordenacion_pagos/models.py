from django.db import models
from django.conf import settings

class SolicitudPago(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente de Revisión'),
        ('autorizado', 'Autorizado para Pago'),
        ('rechazado', 'Rechazado'),
    ]
    
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_vencimiento = models.DateField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    autorizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notas_auditoria = models.TextField(blank=True)

    def __str__(self):
        return f"Solicitud {self.id} - {self.descripcion[:50]}"
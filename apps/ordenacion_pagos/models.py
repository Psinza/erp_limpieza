from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.compras.models import FacturaCompra
from apps.facturacion.models import RetencionIVA, RetencionISLR

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
    
    # Vinculación con facturas de proveedores
    factura_compra = models.ForeignKey(FacturaCompra, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_pago')
    
    # Retenciones aplicadas en este pago
    retencion_iva = models.ForeignKey(RetencionIVA, on_delete=models.SET_NULL, null=True, blank=True)
    retencion_islr = models.ForeignKey(RetencionISLR, on_delete=models.SET_NULL, null=True, blank=True)
    
    monto_pago_neto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Monto a pagar luego de retenciones")

    def __str__(self):
        return f"Solicitud {self.id} - {self.descripcion[:50]}"
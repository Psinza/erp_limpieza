from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrdenCompra, RetencionIVA, RetencionISLR
from decimal import Decimal

@receiver(post_save, sender=OrdenCompra)
def generar_propuestas_retencion(sender, instance, created, **kwargs):
    """
    Cuando una Orden de Compra se marca como 'confirmada' y tiene datos fiscales,
    se generan automáticamente las propuestas de retención de IVA e ISLR.
    """
    if instance.estado == 'confirmada' and instance.nro_factura and instance.nro_control:
        
        # 1. Propuesta de Retención de IVA
        if instance.monto_iva > 0:
            if not RetencionIVA.objects.filter(nro_factura=instance.nro_factura, proveedor=instance.proveedor).exists():
                RetencionIVA.objects.create(
                    nro_comprobante=f"IVA-{instance.id}", # Temporal, debe cambiarse por correlativo oficial
                    proveedor=instance.proveedor,
                    nro_factura=instance.nro_factura,
                    nro_control=instance.nro_control,
                    fecha_factura=instance.fecha_emision,
                    monto_total_compra=instance.total,
                    base_imponible=instance.base_imponible,
                    monto_iva=instance.monto_iva,
                    porcentaje_retencion=instance.proveedor.porcentaje_retencion_iva
                )

        # 2. Propuesta de Retención de ISLR
        # Nota: El código de concepto suele ser '001' (Honorarios) o '019' (Servicios) por defecto.
        if instance.base_imponible > 0:
            if not RetencionISLR.objects.filter(nro_factura=instance.nro_factura, proveedor=instance.proveedor).exists():
                # Determinamos un porcentaje base (ej: 1% para bienes, 3% para servicios)
                # En un caso real, esto vendría de la categoría del ProductoCompra
                RetencionISLR.objects.create(
                    nro_comprobante=f"ISLR-{instance.id}",
                    proveedor=instance.proveedor,
                    nro_factura=instance.nro_factura,
                    nro_control=instance.nro_control,
                    fecha_factura=instance.fecha_emision,
                    codigo_concepto="000", # Pendiente por definir por el usuario
                    monto_operacion=instance.base_imponible,
                    porcentaje_retencion=Decimal('1.00'),
                    sustraendo=Decimal('0.00')
                )
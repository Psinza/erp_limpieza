from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import F
from .models import OrdenProduccion, LoteProduccion, ProductoTerminado

@receiver(post_save, sender=OrdenProduccion)
def crear_lote_automatico(sender, instance, created, **kwargs):
    """
    Crea automáticamente un LoteProduccion cuando una orden pasa al estado 'en_proceso'
    y no tiene lotes previos asignados.
    """
    if instance.estado == 'en_proceso' and not instance.lotes.exists():
        timestamp = timezone.now().strftime('%Y%m%d%H%M')
        # Añadimos segundos para mayor unicidad en el número de lote
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        LoteProduccion.objects.create(
            orden=instance,
            numero_lote=f"LOT-{instance.id:04d}-{timestamp}",
            estado='en_produccion'
        )

@receiver(post_save, sender=LoteProduccion)
def actualizar_stock_producto_terminado(sender, instance, created, **kwargs):
    """
    Actualiza el stock del ProductoTerminado cuando un LoteProduccion es 'liberado'.
    """
    # Solo si el lote está siendo actualizado (no creado) y su estado es 'liberado'
    if not created and instance.estado == 'liberado':
        # Asegurarse de que la transición fue *hacia* 'liberado'
        # Esto evita que se actualice el stock si el lote ya estaba liberado y se guarda de nuevo.
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.estado != 'liberado':
            producto = instance.orden.formula.producto
            # Usar F() para una actualización atómica y evitar condiciones de carrera
            producto.stock_actual = F('stock_actual') + instance.cantidad_final
            producto.save(update_fields=['stock_actual']) # Solo actualiza el campo stock_actual
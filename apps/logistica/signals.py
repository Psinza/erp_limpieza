from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F

from apps.logistica.models import MovimientoInventario
from apps.produccion.models import MateriaPrima, ProductoTerminado


@receiver(post_save, sender=MovimientoInventario)
def update_inventory_on_movement_save(sender, instance, created, **kwargs):
    # Solo procesamos nuevos movimientos.
    # Las actualizaciones de movimientos existentes (especialmente cantidad/tipo)
    # requerirían una lógica compleja para revertir efectos previos y recalcular
    # entradas de saldo_stock subsiguientes, lo cual se maneja típicamente
    # creando nuevos movimientos compensatorios en lugar de modificar entradas históricas del Kardex.
    if not created:
        return

    item = None
    item_model = None
    if instance.materia_prima:
        item = instance.materia_prima
        item_model = MateriaPrima
    elif instance.producto_pt:
        item = instance.producto_pt
        item_model = ProductoTerminado
    else:
        # Este caso idealmente debería ser prevenido por la validación del modelo
        # o un diseño más específico donde un movimiento *debe* estar relacionado con un ítem.
        print(f"Error: MovimientoInventario {instance.pk} no tiene materia prima ni producto terminado asociado.")
        return

    with transaction.atomic():
        # Obtenemos el objeto del ítem de la base de datos y lo bloqueamos para actualización
        # para asegurar que obtenemos el stock_actual más reciente y evitar condiciones de carrera.
        item_obj = item_model.objects.select_for_update().get(pk=item.pk)
        
        stock_change = 0
        if instance.tipo == 'E':  # Entrada
            stock_change = instance.cantidad
        elif instance.tipo == 'S':  # Salida
            stock_change = -instance.cantidad
        # Para 'T' (Transferencia), el stock_actual global no cambia.
        # Si se necesita control de stock por almacén, el diseño del modelo debería ser diferente.

        # Actualizamos el stock_actual global del ítem usando una operación atómica (F()).
        item_obj.stock_actual = F('stock_actual') + stock_change
        item_obj.save(update_fields=['stock_actual'])
        
        # Recargamos item_obj para obtener el nuevo valor de stock_actual después de la actualización atómica.
        item_obj.refresh_from_db()

        # Actualizamos el saldo_stock de la instancia actual de MovimientoInventario
        # para reflejar el stock global después de este movimiento.
        instance.saldo_stock = item_obj.stock_actual
        # Guardamos la instancia de MovimientoInventario, actualizando solo saldo_stock
        # para evitar que esta señal se dispare recursivamente por otros campos.
        instance.save(update_fields=['saldo_stock'])
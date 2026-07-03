from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F

from apps.logistica.models import MovimientoInventario, ExistenciaAlmacen
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

        # 1. Actualización de Stock Global
        stock_change = 0
        if instance.tipo == 'E':  # Entrada
            stock_change = instance.cantidad
        elif instance.tipo == 'S':  # Salida
            stock_change = -instance.cantidad

        if stock_change != 0:
            item_obj.stock_actual = F('stock_actual') + stock_change
            item_obj.save(update_fields=['stock_actual'])
        
        # 2. Actualización de Stock por Almacén (ExistenciaAlmacen)
        item_query = {'materia_prima': instance.materia_prima} if instance.materia_prima else {'producto_pt': instance.producto_pt}

        # Descontar de Origen (Salidas y Transferencias)
        if instance.tipo in ['S', 'T'] and instance.almacen_origen:
            exis_origen, _ = ExistenciaAlmacen.objects.get_or_create(
                almacen=instance.almacen_origen,
                **item_query,
                defaults={'stock': 0}
            )
            ExistenciaAlmacen.objects.filter(pk=exis_origen.pk).update(stock=F('stock') - instance.cantidad)

        # Aumentar en Destino (Entradas y Transferencias)
        if instance.tipo in ['E', 'T'] and instance.almacen_destino:
            exis_destino, _ = ExistenciaAlmacen.objects.get_or_create(
                almacen=instance.almacen_destino,
                **item_query,
                defaults={'stock': 0}
            )
            ExistenciaAlmacen.objects.filter(pk=exis_destino.pk).update(stock=F('stock') + instance.cantidad)

        # Finalización: Actualizar saldo_stock en el movimiento para el Kardex Global
        item_obj.refresh_from_db()
        instance.saldo_stock = item_obj.stock_actual
        instance.save(update_fields=['saldo_stock'])
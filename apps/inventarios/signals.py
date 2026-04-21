@receiver(post_save, sender=OrdenProduccion)
def finalizar_produccion(sender, instance, **kwargs):
    # Si la orden pasa a estado 'completado'
    if instance.estado == 'completado':
        ref = f"PROD-{instance.id}"
        
        if not MovimientoInventario.objects.filter(referencia=ref).exists():
            # 1. SALIDA de Insumos (Materia Prima de Compras)
            for insumo in instance.receta.insumos.all():
                cantidad_a_descontar = insumo.cantidad_necesaria * instance.cantidad_producida
                MovimientoInventario.objects.create(
                    producto_compra=insumo.material,
                    tipo='SALIDA',
                    cantidad=cantidad_a_descontar,
                    referencia=ref,
                    motivo="Consumo Producción"
                )
            
            # 2. ENTRADA de Producto Terminado (Stock de Ventas)
            MovimientoInventario.objects.create(
                producto_venta=instance.producto_final,
                tipo='ENTRADA',
                cantidad=instance.cantidad_producida,
                referencia=ref,
                motivo="Ingreso por Producción"
            )
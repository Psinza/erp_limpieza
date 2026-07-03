from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Factura
from apps.core.models import AsientoContable, LineaAsiento, ConfiguracionContable, EjercicioContable
from apps.logistica.models import MovimientoInventario, Almacen
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Factura)
def actualizar_stock_por_venta(sender, instance, created, **kwargs):
    """
    Al emitir una factura legal VZLA, se genera automáticamente un 
    movimiento de salida en el módulo de logística para descontar el stock.
    """
    if instance.estado in ['EMI', 'PAG']:
        # En VZLA es obligatorio el Nro de Control para el Libro de Ventas
        referencia_venta = f"Factura: {instance.nro_factura} / Control: {instance.nro_control}"
        
        # Evitar duplicados comprobando si ya existe un movimiento con esta referencia
        if not MovimientoInventario.objects.filter(referencia=referencia_venta).exists():
            
            # Buscar el almacén principal de producto terminado
            # Si no existe, usamos el primero disponible o fallamos silenciosamente
            almacen_pt = Almacen.objects.filter(es_principal=True).first() or Almacen.objects.first()
            
            if not almacen_pt:
                logger.error(f"Error stock: No hay almacenes para la factura {instance.nro_factura}")
                return

            for detalle in instance.detalles.all():
                # Obtenemos el producto terminado vinculado al producto de venta
                producto_fabricado = detalle.producto.producto_base
                
                if producto_fabricado:
                    MovimientoInventario.objects.create(
                        producto_pt=producto_fabricado,
                        tipo='S', # Salida
                        motivo='venta',
                        almacen_origen=almacen_pt,
                        cantidad=detalle.cantidad,
                        referencia=referencia_venta,
                        usuario=None, # Podríamos pasar el usuario que emitió
                        fecha=timezone.now()
                    )
                else:
                    logger.warning(f"Producto {detalle.producto.nombre} sin vínculo de stock.")

@receiver(post_save, sender=Factura)
def generar_asiento_contable_venta(sender, instance, created, **kwargs):
    """
    Genera el asiento contable bajo normativa VEN-NIF.
    """
    if instance.estado == 'EMI':
        referencia = f"FACT-{instance.nro_factura}"
        
        with transaction.atomic():
            if AsientoContable.objects.filter(descripcion__icontains=referencia).exists():
                return

            ejercicio = EjercicioContable.objects.filter(cerrado=False).first()
            if not ejercicio:
                logger.error(f"Error legal: No hay ejercicio abierto para la factura {instance.nro_factura}")
                return

            try:
                # Validación de cuentas obligatorias según plan de cuentas local
                cta_ingreso = ConfiguracionContable.objects.get(clave='ingreso_ventas').cuenta
                cta_iva = ConfiguracionContable.objects.get(clave='iva_debito_fiscal').cuenta
                cta_cxc = ConfiguracionContable.objects.get(clave='cuentas_por_cobrar').cuenta
                
                asiento = AsientoContable.objects.create(
                    fecha=instance.fecha_emision,
                    descripcion=f"Venta VZLA {referencia} / Ctrl: {instance.nro_control} - {instance.cliente.nombre}",
                    ejercicio=ejercicio,
                    estado='aprobado'
                )

                monto_base = getattr(instance, 'monto_base', 0)
                monto_iva = getattr(instance, 'monto_iva', 0)
                monto_total = getattr(instance, 'total', 0)

                # Partida Doble: DEBE (CxC) = HABER (Ventas + IVA)
                LineaAsiento.objects.create(asiento=asiento, cuenta=cta_cxc, debe=monto_total, haber=0)
                LineaAsiento.objects.create(asiento=asiento, cuenta=cta_ingreso, debe=0, haber=monto_base)
                LineaAsiento.objects.create(asiento=asiento, cuenta=cta_iva, debe=0, haber=monto_iva)
                
                logger.info(f"Asiento generado exitosamente para factura {instance.nro_factura}")
                
            except ConfiguracionContable.DoesNotExist as e:
                logger.error(f"Configuración contable incompleta: {str(e)}")
                # En producción esto debería notificar al administrador
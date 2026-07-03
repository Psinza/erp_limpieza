from decimal import Decimal
from django.utils import timezone
from .models import Vendedor, Comision
from django.db.models import Sum
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class ComisionService:
    @staticmethod
    @transaction.atomic
    def calcular_comision_venta(usuario_vendedor, venta_id, monto_total):
        """
        Calcula y registra la comisión para una venta específica.
        """
        try:
            vendedor = usuario_vendedor.vendedor
        except Vendedor.DoesNotExist:
            logger.error(f"Fallo al calcular comisión: Usuario {usuario_vendedor} no es vendedor.")
            return None

        if not vendedor.activo:
            logger.warning(f"Intento de comisión para vendedor inactivo: {vendedor}")
            return None

        monto_comision = (monto_total * vendedor.comision_porcentaje) / Decimal('100.00')

        logger.info(f"Generando comisión de {monto_comision} para {vendedor} por venta {venta_id}")
        comision = Comision.objects.create(
            vendedor=vendedor,
            pedido_venta_id=venta_id,
            monto_venta=monto_total,
            base_imponible=monto_total,
            porcentaje_aplicado=vendedor.comision_porcentaje,
            monto_comision=monto_comision
        )
        return comision

    @staticmethod
    @transaction.atomic
    def verificar_cumplimiento_meta(vendedor_instancia, mes, anio):
        """
        Revisa si el vendedor alcanzó su meta mensual definida en su perfil.
        """
        if vendedor_instancia.meta_mensual <= 0:
            return False

        # Sumamos el total de los pedidos asociados a sus comisiones en el mes
        total_vendido = Comision.objects.filter(
            vendedor=vendedor_instancia, 
            fecha_calculo__month=mes, 
            fecha_calculo__year=anio
        ).aggregate(total=Sum('monto_venta'))['total'] or Decimal('0.00')

        if total_vendido >= vendedor_instancia.meta_mensual:
            return True
        return False

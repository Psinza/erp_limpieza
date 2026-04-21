from decimal import Decimal
from .models import VendedorProfile, Comision, MetaVendedor
from django.db.models import Sum
from django.db import transaction

class ComisionService:
    @staticmethod
    @transaction.atomic
    def calcular_comision_venta(usuario_vendedor, venta_id, monto_total):
        """
        Calcula y registra la comisión para una venta específica.
        """
        try:
            perfil = usuario_vendedor.perfil_vendedor
        except VendedorProfile.DoesNotExist:
            return None

        if not perfil.activo:
            return None

        monto_comision = (monto_total * perfil.porcentaje_comision_base) / Decimal('100.00')

        comision = Comision.objects.create(
            vendedor=perfil,
            venta_id=venta_id,
            monto_venta=monto_total,
            porcentaje_aplicado=perfil.porcentaje_comision_base,
            monto_comision=monto_comision
        )
        return comision

    @staticmethod
    @transaction.atomic
    def verificar_cumplimiento_meta(vendedor, mes, anio):
        """
        Revisa si el vendedor alcanzó su meta mensual y marca el bono.
        """
        meta = MetaVendedor.objects.filter(vendedor=vendedor, mes=mes, anio=anio).first()
        if not meta:
            return False

        total_vendido = Comision.objects.filter(
            vendedor=vendedor, 
            fecha_creacion__month=mes, 
            fecha_creacion__year=anio
        ).aggregate(total=Sum('monto_venta'))['total'] or Decimal('0.00')

        if total_vendido >= meta.monto_meta:
            meta.alcanzada = True
            meta.save()
            return True
        return False
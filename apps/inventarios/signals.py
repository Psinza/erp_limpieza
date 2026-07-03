from django.db.models.signals import post_save
from django.dispatch import receiver

# TODO: Refactorizar señales para que se adapten al nuevo modelo de FacturaCompra.
# from apps.compras.models import FacturaCompra
# from .models import MovimientoInventario

# @receiver(post_save, sender=FacturaCompra)
# def registrar_recepcion_aprobada(sender, instance, **kwargs):
#     pass

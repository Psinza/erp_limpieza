from django.db.models import Sum

from .models import MovimientoInventario


def obtener_stock_actual(producto_id):
    entradas = MovimientoInventario.objects.filter(
        producto_id=producto_id, tipo='ENTRADA'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    salidas = MovimientoInventario.objects.filter(
        producto_id=producto_id, tipo='SALIDA'
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    return entradas - salidas


def obtener_valor_inventario(producto_id):
    entradas = MovimientoInventario.objects.filter(producto_id=producto_id, tipo='ENTRADA')
    return sum(mov.valor_total for mov in entradas)

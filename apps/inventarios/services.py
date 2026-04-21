from django.db.models import Sum

def obtener_stock_actual(producto_id):
    entradas = MovimientoInventario.objects.filter(
        producto_id=producto_id, tipo='ENTRADA'
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    salidas = MovimientoInventario.objects.filter(
        producto_id=producto_id, tipo='SALIDA'
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    return entradas - salidas
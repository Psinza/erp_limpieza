from django.views.generic import ListView
from django.db.models import Sum, Q
from apps.compras.models import ProductoCompra

class InventarioGlobalListView(ListView):
    model = ProductoCompra
    template_name = 'inventarios/stock_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        # Esta consulta es "Oro puro": calcula el stock real al vuelo
        return ProductoCompra.objects.filter(activo=True).annotate(
            total_entradas=Sum('movimientos__cantidad', filter=Q(movimientos__tipo='ENTRADA')),
            total_salidas=Sum('movimientos__cantidad', filter=Q(movimientos__tipo='SALIDA'))
        ).order_by('nombre')
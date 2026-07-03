from django.db.models import DecimalField, ExpressionWrapper, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.views.generic import ListView

from apps.compras.models import ProductoCompra


class InventarioGlobalListView(ListView):
    model = ProductoCompra
    template_name = 'inventarios/stock_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return ProductoCompra.objects.annotate(
            total_entradas=Coalesce(
                Sum('movimientos__cantidad', filter=Q(movimientos__tipo='ENTRADA')),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            total_salidas=Coalesce(
                Sum('movimientos__cantidad', filter=Q(movimientos__tipo='SALIDA')),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        ).annotate(
            stock_actual=ExpressionWrapper(
                Coalesce('total_entradas', Value(0)) - Coalesce('total_salidas', Value(0)),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ).order_by('nombre')

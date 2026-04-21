from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from .models import Vendedor, Comision

@login_required
def dashboard_vendedores(request):
    """Dashboard para ver el rendimiento de todos los vendedores (Vista Admin)."""
    vendedores = Vendedor.objects.all().select_related('usuario')
    hoy = timezone.now()
    
    # Resumen general
    total_comisiones = Comision.objects.filter(pagado=False).aggregate(Sum('monto_comision'))['monto_comision__sum'] or 0
    
    context = {
        'vendedores': vendedores,
        'total_comisiones_pendientes': total_comisiones,
        'mes_actual': hoy.strftime('%B %Y')
    }
    return render(request, 'vendedores/dashboard.html', context)

@login_required
def mi_rendimiento(request):
    """Dashboard individual para el vendedor logueado."""
    vendedor = get_object_or_404(Vendedor, usuario=request.user)
    hoy = timezone.now()
    
    comisiones = Comision.objects.filter(vendedor=vendedor, fecha_calculo__month=hoy.month)
    total_ganado = comisiones.aggregate(Sum('monto_comision'))['monto_comision__sum'] or Decimal('0.00')
    
    # Calcular progreso hacia la meta
    progreso = 0
    if vendedor.meta_mensual > 0:
        # Aquí asumo que la meta se mide contra el total vendido. 
        # Por ahora usaremos un valor simulado o basado en pedidos si existen.
        progreso = min(int((total_ganado / vendedor.meta_mensual) * 1000), 100) # Ajuste de escala simulado
    
    context = {
        'vendedor': vendedor,
        'comisiones': comisiones.order_by('-fecha_calculo')[:10],
        'total_ganado': total_ganado,
        'progreso': progreso,
    }
    return render(request, 'vendedores/mi_rendimiento.html', context)
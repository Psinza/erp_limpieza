from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import FacturaVenta
from apps.ventas.models import Cotizacion, Despacho

from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime

@login_required
def dashboard(request):
    """Panel principal del módulo de Facturación."""
    hoy = timezone.now()
    facturas_mes = FacturaVenta.objects.filter(
        fecha_emision__year=hoy.year, 
        fecha_emision__month=hoy.month,
        anulada=False
    )
    
    stats = {
        'ventas_mes': facturas_mes.aggregate(total=Sum('total'))['total'] or 0.00,
        'presupuestos_activos': Cotizacion.objects.filter(estado__in=['enviada', 'aceptada']).count(),
        'notas_entrega_pendientes': Despacho.objects.filter(estado='preparando').count(),
        'iva_por_pagar': facturas_mes.aggregate(
            iva=(Sum('monto_iva_general') + Sum('monto_iva_reducida') + Sum('monto_iva_suntuaria'))
        )['iva'] or 0.00,
    }
    
    facturas_recientes = FacturaVenta.objects.all().order_by('-fecha_emision')[:5]
    return render(request, 'facturacion/dashboard.html', {
        'titulo': 'Facturación y Cobranzas', 
        'stats': stats,
        'facturas_recientes': facturas_recientes
    })

@login_required
def factura_list(request):
    facturas = FacturaVenta.objects.all().order_by('-fecha_emision')
    return render(request, 'facturacion/factura_list.html', {'facturas': facturas, 'titulo': 'Facturas Fiscales'})

@login_required
def factura_create(request):
    from .forms import FacturaVentaForm
    if request.method == 'POST':
        form = FacturaVentaForm(request.POST)
        if form.is_valid():
            factura = form.save()
            return redirect('facturacion:factura_list')
    else:
        form = FacturaVentaForm(initial={'fecha_emision': timezone.now().date()})
    return render(request, 'facturacion/factura_form.html', {'form': form, 'titulo': 'Emitir Factura Fiscal'})

@login_required
def presupuesto_create(request):
    # Redirigir al módulo de ventas para crear cotización
    return redirect('ventas:cotizacion_create')

@login_required
def nota_entrega_create(request):
    # Redirigir al módulo de ventas para crear despacho
    return redirect('ventas:pedido_list') # O crear una vista específica si existe

@login_required
def presupuesto_list(request):
    presupuestos = Cotizacion.objects.all().order_by('-fecha_emision')
    return render(request, 'facturacion/presupuesto_list.html', {'presupuestos': presupuestos, 'titulo': 'Presupuestos / Cotizaciones'})

@login_required
def nota_entrega_list(request):
    notas = Despacho.objects.all().order_by('-fecha_despacho')
    return render(request, 'facturacion/nota_entrega_list.html', {'notas': notas, 'titulo': 'Notas de Entrega / Guías'})

@login_required
def libro_ventas(request):
    """Genera el Libro de Ventas mensual según normativa SENIAT."""
    mes = request.GET.get('mes', timezone.now().month)
    anio = request.GET.get('anio', timezone.now().year)
    
    facturas = FacturaVenta.objects.filter(
        fecha_emision__year=anio, 
        fecha_emision__month=mes
    ).order_by('numero_factura')
    
    resumen = {
        'total_ventas': facturas.filter(anulada=False).aggregate(Sum('total'))['total__sum'] or 0,
        'total_base': facturas.filter(anulada=False).aggregate(Sum('base_imponible'))['base_imponible__sum'] or 0,
        'total_iva': facturas.filter(anulada=False).aggregate(
            iva=Sum('monto_iva_general') + Sum('monto_iva_reducida')
        )['iva'] or 0,
        'total_exento': facturas.filter(anulada=False).aggregate(Sum('exento'))['exento__sum'] or 0,
        'total_igtf': facturas.filter(anulada=False).aggregate(Sum('monto_igtf'))['monto_igtf__sum'] or 0,
    }
    
    return render(request, 'facturacion/libro_ventas.html', {
        'facturas': facturas,
        'resumen': resumen,
        'mes': int(mes),
        'anio': int(anio),
        'meses': range(1, 13)
    })

from .models_correlativos import CorrelativoFiscal

@login_required
def configurar_correlativos(request):
    tipos = ['factura', 'control', 'nota_entrega', 'presupuesto']
    for t in tipos:
        CorrelativoFiscal.objects.get_or_create(tipo=t)
    
    if request.method == 'POST':
        for c in CorrelativoFiscal.objects.all():
            prefijo = request.POST.get(f'prefijo_{c.id}')
            proximo = request.POST.get(f'proximo_{c.id}')
            if prefijo is not None:
                c.prefijo = prefijo
            if proximo:
                c.proximo_numero = int(proximo)
            c.save()
        return redirect('facturacion:configurar_correlativos')
        
    correlativos = CorrelativoFiscal.objects.all()
    return render(request, 'facturacion/configurar_correlativos.html', {'correlativos': correlativos})
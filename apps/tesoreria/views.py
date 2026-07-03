from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.core.models import CuentaContable, AsientoContable, LineaAsiento
from apps.tesoreria.models import CuentaPorCobrar, CuentaPorPagar

@login_required
def dashboard(request):
    """Panel principal del módulo de Tesorería con datos reales de la contabilidad."""
    hoy = timezone.now().date()
    
    # 1. Cálculo de saldos reales basados en el Plan de Cuentas
    # Filtramos por tipo activo y nombres comunes (esto se puede mejorar usando códigos específicos)
    saldo_bancos = CuentaContable.objects.filter(
        tipo='activo', 
        nombre__icontains='banco'
    ).aggregate(total=Sum('saldo_actual'))['total'] or 0
    
    saldo_caja = CuentaContable.objects.filter(
        tipo='activo', 
        nombre__icontains='caja'
    ).aggregate(total=Sum('saldo_actual'))['total'] or 0
    
    # 2. Métricas de documentos
    pagos_pendientes = AsientoContable.objects.filter(estado='borrador').count()
    
    # Cobros del día: Asientos aprobados hoy que afectan cuentas de ingresos
    cobros_hoy = AsientoContable.objects.filter(
        fecha=hoy, 
        estado='aprobado',
        lineas__cuenta__tipo='ingreso'
    ).distinct().count()

    stats = {
        'saldo_bancos': float(saldo_bancos),
        'saldo_caja': float(saldo_caja),
        'pagos_pendientes': pagos_pendientes,
        'cobros_hoy': cobros_hoy
    }

    # 3. Data para el gráfico de barras: Ventas de los últimos 6 meses
    hace_6_meses = hoy - timedelta(days=180)
    ventas_query = LineaAsiento.objects.filter(
        cuenta__tipo='ingreso',
        asiento__fecha__gte=hace_6_meses,
        asiento__estado='aprobado'
    ).annotate(mes=TruncMonth('asiento__fecha')).values('mes').annotate(total=Sum('haber')).order_by('mes')

    chart_labels = [v['mes'].strftime('%b %Y') for v in ventas_query]
    chart_data = [float(v['total']) for v in ventas_query]

    # 4. Proyección de Flujo de Caja (Próximos 4 meses)
    proyeccion_labels = []
    ingresos_proy = []
    egresos_proy = []
    alertas_flujo = []

    for i in range(1, 5):
        fecha_proy = hoy + timedelta(days=30*i)
        inicio_mes = fecha_proy.replace(day=1)
        fin_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        mes_nombre = inicio_mes.strftime('%b %Y')
        proyeccion_labels.append(mes_nombre)

        # Consultamos vencimientos reales en este rango de fechas
        ing = CuentaPorCobrar.objects.filter(
            fecha_vencimiento__range=[inicio_mes, fin_mes],
            estado__in=['pend', 'parcial']
        ).aggregate(total=Sum('saldo_pendiente'))['total'] or 0
        
        egr = CuentaPorPagar.objects.filter(
            fecha_vencimiento__range=[inicio_mes, fin_mes],
            estado__in=['pend', 'parcial']
        ).aggregate(total=Sum('saldo_pendiente'))['total'] or 0

        ingresos_proy.append(ing)
        egresos_proy.append(egr)

        if egr > ing:
            alertas_flujo.append({'mes': mes_nombre, 'deficit': egr - ing})

    return render(request, 'tesoreria/dashboard.html', {
        'titulo': 'Caja y Bancos', 
        'stats': stats,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'proyeccion_labels': proyeccion_labels,
        'ingresos_proy': ingresos_proy,
        'egresos_proy': egresos_proy,
        'alertas_flujo': alertas_flujo,
    })


# ─── Cuentas por Cobrar ──────────────────────────────────────────────────────
@login_required
def cxc_list(request):
    try:
        cxc = CuentaPorCobrar.objects.order_by('-fecha_emision')
    except Exception:
        cxc = []
    return render(request, 'tesoreria/cxc_list.html', {'titulo': 'Cuentas por Cobrar', 'cxc': cxc})

@login_required
def cxc_create(request):
    return render(request, 'tesoreria/cxc_form.html', {'titulo': 'Nueva Cuenta por Cobrar'})

@login_required
def cxc_detail(request, pk):
    try:
        cxc = CuentaPorCobrar.objects.get(pk=pk)
    except Exception:
        cxc = None
    return render(request, 'tesoreria/cxc_detail.html', {'titulo': 'Detalle CxC', 'cxc': cxc})


# ─── Cuentas por Pagar ───────────────────────────────────────────────────────
@login_required
def cxp_list(request):
    try:
        cxp = CuentaPorPagar.objects.order_by('-fecha_emision')
    except Exception:
        cxp = []
    return render(request, 'tesoreria/cxp_list.html', {'titulo': 'Cuentas por Pagar', 'cxp': cxp})

@login_required
def cxp_create(request):
    return render(request, 'tesoreria/cxp_form.html', {'titulo': 'Nueva Cuenta por Pagar'})

@login_required
def cxp_detail(request, pk):
    try:
        cxp = CuentaPorPagar.objects.get(pk=pk)
    except Exception:
        cxp = None
    return render(request, 'tesoreria/cxp_detail.html', {'titulo': 'Detalle CxP', 'cxp': cxp})


# ─── Bancos y Cuentas Bancarias ──────────────────────────────────────────────
@login_required
def banco_list(request):
    try:
        from apps.tesoreria.models import Banco
        bancos = Banco.objects.all()
    except Exception:
        bancos = []
    return render(request, 'tesoreria/banco_list.html', {'titulo': 'Bancos', 'bancos': bancos})

@login_required
def banco_create(request):
    return render(request, 'tesoreria/banco_form.html', {'titulo': 'Nuevo Banco'})

@login_required
def cuenta_list(request):
    try:
        from apps.tesoreria.models import CuentaBancaria
        cuentas = CuentaBancaria.objects.all()
    except Exception:
        cuentas = []
    return render(request, 'tesoreria/cuenta_list.html', {'titulo': 'Cuentas Bancarias', 'cuentas': cuentas})

@login_required
def cuenta_create(request):
    return render(request, 'tesoreria/cuenta_form.html', {'titulo': 'Nueva Cuenta Bancaria'})

@login_required
def cuenta_detail(request, pk):
    return render(request, 'tesoreria/cuenta_detail.html', {'titulo': 'Detalle de Cuenta'})


# ─── Cajas ───────────────────────────────────────────────────────────────────
@login_required
def caja_list(request):
    try:
        from apps.tesoreria.models import Caja
        cajas = Caja.objects.all()
    except Exception:
        cajas = []
    return render(request, 'tesoreria/caja_list.html', {'titulo': 'Cajas', 'cajas': cajas})

@login_required
def caja_create(request):
    return render(request, 'tesoreria/caja_form.html', {'titulo': 'Nueva Caja'})

@login_required
def caja_detail(request, pk):
    return render(request, 'tesoreria/caja_detail.html', {'titulo': 'Detalle de Caja'})

@login_required
def movimiento_caja_create(request):
    return render(request, 'tesoreria/movimiento_caja_form.html', {'titulo': 'Nuevo Movimiento de Caja'})


# ─── Transferencias ──────────────────────────────────────────────────────────
@login_required
def transferencia_list(request):
    try:
        from apps.tesoreria.models import TransferenciaBancaria
        transferencias = TransferenciaBancaria.objects.order_by('-fecha')
    except Exception:
        transferencias = []
    return render(request, 'tesoreria/transferencia_list.html', {'titulo': 'Transferencias', 'transferencias': transferencias})

@login_required
def transferencia_create(request):
    return render(request, 'tesoreria/transferencia_form.html', {'titulo': 'Nueva Transferencia'})


# ─── Reportes ────────────────────────────────────────────────────────────────
@login_required
def flujo_caja(request):
    return render(request, 'tesoreria/flujo_caja.html', {'titulo': 'Flujo de Caja Proyectado'})
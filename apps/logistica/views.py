from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """Panel principal del módulo de Logística."""
    try:
        from apps.logistica.models import Almacen, MovimientoInventario, ExistenciaAlmacen
        from apps.produccion.models import MateriaPrima, ProductoTerminado
        from django.db.models import Sum

        almacenes = Almacen.objects.all()
        movimientos_recientes = MovimientoInventario.objects.order_by('-fecha')[:10]

        # Valor total de MP basado en existencias
        valor_total_mp = ExistenciaAlmacen.objects.aggregate(
            total=Sum('cantidad')
        )['total'] or 0

        # Alertas de stock bajo
        materias_primas_alerta = MateriaPrima.objects.filter(
            stock_actual__lte=10
        )
        alerta_mp = materias_primas_alerta.count()
        total_pt = ProductoTerminado.objects.count()
    except Exception:
        almacenes = []
        movimientos_recientes = []
        valor_total_mp = 0
        materias_primas_alerta = []
        alerta_mp = 0
        total_pt = 0

    return render(request, 'logistica/dashboard.html', {
        'titulo': 'Inventario y Almacén',
        'almacenes': almacenes,
        'movimientos_recientes': movimientos_recientes,
        'valor_total_mp': valor_total_mp,
        'materias_primas_alerta': materias_primas_alerta,
        'alerta_mp': alerta_mp,
        'total_pt': total_pt,
    })


@login_required
def movimiento_list(request):
    try:
        from apps.logistica.models import MovimientoInventario
        movimientos = MovimientoInventario.objects.order_by('-fecha')
    except Exception:
        movimientos = []
    return render(request, 'logistica/movimiento_list.html', {
        'titulo': 'Movimientos de Inventario',
        'movimientos': movimientos,
    })


@login_required
def movimiento_create(request):
    from .forms import MovimientoInventarioForm
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.usuario = request.user
            mov.save()
            return redirect('logistica:movimiento_list')
    else:
        form = MovimientoInventarioForm()
    return render(request, 'logistica/movimiento_form.html', {
        'titulo': 'Nuevo Movimiento de Inventario',
        'form': form
    })


@login_required
def almacen_list(request):
    try:
        from apps.logistica.models import Almacen
        almacenes = Almacen.objects.all()
    except Exception:
        almacenes = []
    return render(request, 'logistica/almacen_list.html', {
        'titulo': 'Gestión de Almacenes',
        'almacenes': almacenes,
    })


@login_required
def almacen_create(request):
    from .forms import AlmacenForm
    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logistica:almacen_list')
    else:
        form = AlmacenForm()
    return render(request, 'logistica/almacen_form.html', {
        'titulo': 'Nuevo Almacén',
        'form': form
    })


@login_required
def almacen_update(request, pk):
    from .models import Almacen
    from .forms import AlmacenForm
    almacen = get_object_or_404(Almacen, pk=pk)
    if request.method == 'POST':
        form = AlmacenForm(request.POST, instance=almacen)
        if form.is_valid():
            form.save()
            return redirect('logistica:almacen_list')
    else:
        form = AlmacenForm(instance=almacen)
    return render(request, 'logistica/almacen_form.html', {
        'titulo': 'Editar Almacén',
        'form': form
    })


@login_required
def reporte_stock(request):
    try:
        from apps.logistica.models import ExistenciaAlmacen
        existencias = ExistenciaAlmacen.objects.select_related('almacen').all()
    except Exception:
        existencias = []
    return render(request, 'logistica/reporte_stock.html', {
        'titulo': 'Reporte de Existencias',
        'existencias': existencias,
    })


@login_required
def reporte_kardex(request):
    try:
        from apps.logistica.models import MovimientoInventario
        movimientos = MovimientoInventario.objects.order_by('-fecha')
    except Exception:
        movimientos = []
    return render(request, 'logistica/reporte_kardex.html', {
        'titulo': 'Reporte Kardex',
        'movimientos': movimientos,
    })


@login_required
def transferencia_create(request):
    return render(request, 'logistica/transferencia_form.html', {
        'titulo': 'Nueva Transferencia entre Almacenes',
    })
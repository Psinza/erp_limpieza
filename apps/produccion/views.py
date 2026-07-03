from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import OrdenProduccion, Formula, ProductoTerminado, MateriaPrima
from .forms import OrdenProduccionForm, FormulaForm

@login_required
def dashboard(request):
    """Panel principal del módulo de Producción."""
    try:
        from apps.produccion.models import OrdenProduccion, MateriaPrima, ProductoTerminado
        stats = {
            'activas': OrdenProduccion.objects.filter(estado='en_proceso').count(),
            'planificadas': OrdenProduccion.objects.filter(estado='planificada').count(),
            'alertas_stock': MateriaPrima.objects.filter(stock_actual__lte=10).count(),
            'productos_count': ProductoTerminado.objects.count(),
        }
        ordenes_recientes = list(OrdenProduccion.objects.select_related('formula__producto').order_by('-id')[:5])
        alertas_stock = list(MateriaPrima.objects.filter(stock_actual__lte=10)[:5])
    except Exception:
        stats = {'activas': 0, 'planificadas': 0, 'alertas_stock': 0, 'productos_count': 0}
        ordenes_recientes = []
        alertas_stock = []

    return render(request, 'produccion/dashboard_produccion.html', {
        'titulo': 'Control de Producción',
        'stats': stats,
        'ordenes_recientes': ordenes_recientes,
        'alertas_stock': alertas_stock,
    })


@login_required
def orden_list(request):
    try:
        from apps.produccion.models import OrdenProduccion
        ordenes = OrdenProduccion.objects.all().order_by('-id')
    except Exception:
        ordenes = []
    return render(request, 'produccion/orden_list.html', {'titulo': 'Órdenes de Producción', 'ordenes': ordenes})


@login_required
def orden_create(request):
    if request.method == 'POST':
        form = OrdenProduccionForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.responsable = request.user
            orden.save()
            return redirect('produccion:orden_list')
    else:
        form = OrdenProduccionForm()
    return render(request, 'produccion/orden_form.html', {'titulo': 'Nueva Orden de Producción', 'form': form})


@login_required
def orden_detail(request, pk):
    try:
        from apps.produccion.models import OrdenProduccion
        orden = get_object_or_404(OrdenProduccion, pk=pk)
    except Exception:
        orden = None
    return render(request, 'produccion/orden_detail.html', {'titulo': 'Detalle de Orden', 'orden': orden})


@login_required
def materia_prima_list(request):
    try:
        from apps.produccion.models import MateriaPrima
        materias = MateriaPrima.objects.all().order_by('nombre')
    except Exception:
        materias = []
    return render(request, 'produccion/materia_prima_list.html', {'titulo': 'Materias Primas', 'materias': materias})


@login_required
def formula_list(request):
    try:
        from apps.produccion.models import Formula
        formulas = Formula.objects.all()
    except Exception:
        formulas = []
    return render(request, 'produccion/formula_list.html', {'titulo': 'Fórmulas Maestras', 'formulas': formulas})


@login_required
def producto_terminado_list(request):
    try:
        from apps.produccion.models import ProductoTerminado
        productos = ProductoTerminado.objects.all()
    except Exception:
        productos = []
    return render(request, 'produccion/producto_terminado_list.html', {'titulo': 'Productos Terminados', 'productos': productos})


@login_required
def formula_create(request):
    if request.method == 'POST':
        form = FormulaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('produccion:formula_list')
    else:
        form = FormulaForm()
    return render(request, 'produccion/formula_form.html', {'titulo': 'Nueva Fórmula', 'form': form})


@login_required
def formula_detail(request, pk):
    formula = get_object_or_404(Formula, pk=pk)
    return render(request, 'produccion/formula_detail.html', {'titulo': f'Detalle: {formula.nombre}', 'formula': formula})


@login_required
def formula_update(request, pk):
    formula = get_object_or_404(Formula, pk=pk)
    if request.method == 'POST':
        form = FormulaForm(request.POST, instance=formula)
        if form.is_valid():
            form.save()
            return redirect('produccion:formula_list')
    else:
        form = FormulaForm(instance=formula)
    return render(request, 'produccion/formula_form.html', {'titulo': 'Editar Fórmula', 'form': form})


@login_required
def producto_terminado_create(request):
    # Usaremos el mismo patrón que otros formularios
    # Si no hay formulario específico, podríamos usar uno genérico o crearlo
    # Por ahora asumo que existe o lo crearé si es necesario
    return render(request, 'core/en_construccion.html', {'nombre_modulo': 'Crear Producto Terminado'})
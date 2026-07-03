from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import ActivoFijo, MantenimientoActivo
from .forms import ActivoFijoForm, AsignacionActivoForm, MantenimientoActivoForm

@login_required
def dashboard(request):
    """Panel principal del módulo de Activos Fijos."""
    activos_qs = ActivoFijo.objects.all()
    total_activos = activos_qs.count()
    valor_compra = activos_qs.aggregate(t=Sum('valor_compra'))['t'] or 0
    
    # Cálculo de depreciación para todos los activos
    depreciacion_total = sum(a.depreciacion_acumulada for a in activos_qs)
    valor_libro_total = float(valor_compra) - float(depreciacion_total)
    
    activos_recientes = activos_qs.order_by('-fecha_adquisicion')[:5]
    mantenimientos_proximos = MantenimientoActivo.objects.filter(
        proximo_mantenimiento__gte=timezone.now().date()
    ).order_by('proximo_mantenimiento')[:5]

    return render(request, 'activos_fijos/dashboard.html', {
        'titulo': 'Control de Activos Fijos',
        'stats': {
            'total_activos': total_activos,
            'valor_compra': valor_compra,
            'depreciacion_total': depreciacion_total,
            'valor_libro_total': valor_libro_total,
        },
        'activos_recientes': activos_recientes,
        'mantenimientos_proximos': mantenimientos_proximos,
    })

@login_required
def activo_list(request):
    activos = ActivoFijo.objects.all().order_by('codigo')
    return render(request, 'activos_fijos/activo_list.html', {'titulo': 'Inventario de Activos', 'activos': activos})

@login_required
def activo_create(request):
    if request.method == 'POST':
        form = ActivoFijoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('activos_fijos:activo_list')
    else:
        form = ActivoFijoForm(initial={'fecha_adquisicion': timezone.now().date()})
    return render(request, 'activos_fijos/activo_form.html', {'form': form, 'titulo': 'Registrar Activo Fijo'})

@login_required
def activo_detail(request, pk):
    activo = get_object_or_404(ActivoFijo, pk=pk)
    return render(request, 'activos_fijos/activo_detail.html', {'titulo': 'Detalle de Activo', 'activo': activo})

@login_required
def activo_edit(request, pk):
    activo = get_object_or_404(ActivoFijo, pk=pk)
    if request.method == 'POST':
        form = ActivoFijoForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            return redirect('activos_fijos:activo_detail', pk=pk)
    else:
        form = ActivoFijoForm(instance=activo)
    return render(request, 'activos_fijos/activo_form.html', {'form': form, 'titulo': 'Editar Activo Fijo'})

@login_required
def activo_delete(request, pk):
    activo = get_object_or_404(ActivoFijo, pk=pk)
    if request.method == 'POST':
        activo.delete()
        return redirect('activos_fijos:activo_list')
    return render(request, 'activos_fijos/activo_confirm_delete.html', {'activo': activo, 'titulo': 'Eliminar Activo'})

@login_required
def reporte_depreciacion(request):
    activos = ActivoFijo.objects.all().order_by('categoria', 'codigo')
    return render(request, 'activos_fijos/reporte_depreciacion.html', {
        'titulo': 'Reporte de Depreciación',
        'activos': activos,
    })

@login_required
def asignacion_create(request, pk):
    activo = get_object_or_404(ActivoFijo, pk=pk)
    if request.method == 'POST':
        form = AsignacionActivoForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.activo = activo
            asignacion.save()
            return redirect('activos_fijos:activo_detail', pk=pk)
    else:
        form = AsignacionActivoForm(initial={'fecha_asignacion': timezone.now().date()})
    return render(request, 'activos_fijos/asignacion_form.html', {'form': form, 'activo': activo, 'titulo': 'Asignar Activo'})

@login_required
def mantenimiento_create(request, pk):
    activo = get_object_or_404(ActivoFijo, pk=pk)
    if request.method == 'POST':
        form = MantenimientoActivoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.activo = activo
            mantenimiento.save()
            return redirect('activos_fijos:activo_detail', pk=pk)
    else:
        form = MantenimientoActivoForm(initial={'fecha_mantenimiento': timezone.now().date()})
    return render(request, 'activos_fijos/mantenimiento_form.html', {'form': form, 'activo': activo, 'titulo': 'Registrar Mantenimiento'})
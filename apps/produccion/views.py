from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, F # Import ControlCalidad and ControlCalidadForm
from .models import OrdenProduccion, Formula, ConsumoMateriaPrima, MateriaPrima, LoteProduccion, ControlCalidad
from .forms import ControlCalidadForm, FormulaForm, OrdenProduccionForm

@login_required
def dashboard_produccion(request):
    """Panel principal con indicadores clave y alertas de producción."""
    # 1. Órdenes en curso (En Proceso o Pausadas)
    ordenes_en_curso = OrdenProduccion.objects.filter(
        estado__in=['en_proceso', 'pausada']
    ).select_related('formula__producto').order_by('-fecha_inicio')

    # 2. Alertas de stock bajo (donde stock_actual <= stock_minimo)
    alertas_stock = MateriaPrima.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).select_related('categoria').order_by('stock_actual')

    # 3. Lotes pendientes de QC (En producción o esperando en control)
    lotes_pendientes_qc = LoteProduccion.objects.filter(
        estado__in=['en_produccion', 'en_control_qc']
    ).select_related('orden__formula__producto').order_by('fecha_creacion')

    context = {
        'titulo': 'Dashboard de Producción',
        'ordenes_en_curso': ordenes_en_curso,
        'alertas_stock': alertas_stock,
        'lotes_pendientes_qc': lotes_pendientes_qc,
        'stats': {
            'ordenes_count': ordenes_en_curso.count(),
            'alertas_count': alertas_stock.count(),
            'lotes_count': lotes_pendientes_qc.count(),
        }
    }
    return render(request, 'produccion/dashboard_produccion.html', context)

@login_required
def materia_prima_list(request):
    materias = MateriaPrima.objects.all().select_related('categoria').order_by('nombre')
    return render(request, 'produccion/materia_prima_list.html', {
        'materias': materias,
        'titulo': 'Materias Primas'
    })

@login_required
def producto_terminado_list(request):
    productos = ProductoTerminado.objects.all().order_by('nombre')
    return render(request, 'produccion/producto_terminado_list.html', {
        'productos': productos,
        'titulo': 'Productos Terminados'
    })

@login_required
def formula_list(request):
    formulas = Formula.objects.all().order_by('-id')
    return render(request, 'produccion/formula_list.html', {
        'formulas': formulas,
        'titulo': 'Fórmulas'
    })

@login_required
def formula_create(request):
    if request.method == 'POST':
        form = FormulaForm(request.POST)
        if form.is_valid():
            formula = form.save()
            messages.success(request, f'Fórmula {formula.codigo} creada correctamente.')
            return redirect('produccion:formula_list')
    else:
        form = FormulaForm()
    return render(request, 'produccion/formula_form.html', {
        'form': form,
        'titulo': 'Nueva Fórmula'
    })

@login_required
def orden_create(request):
    if request.method == 'POST':
        form = OrdenProduccionForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.cantidad_a_producir = form.cleaned_data['cantidad_planificada']
            orden.save()
            messages.success(request, f'Orden OP-{orden.id} creada correctamente.')
            return redirect('produccion:orden_list')
    else:
        form = OrdenProduccionForm()
    return render(request, 'produccion/orden_form.html', {
        'form': form,
        'titulo': 'Nueva Orden de Producción'
    })

@login_required
def alerta_stock_list(request):
    alertas_stock = MateriaPrima.objects.filter(stock_actual__lte=F('stock_minimo')).select_related('categoria').order_by('stock_actual')
    return render(request, 'produccion/alerta_stock_list.html', {
        'alertas_stock': alertas_stock,
        'titulo': 'Alertas de Stock'
    })

@login_required
def lotes_qc_list(request):
    lotes = LoteProduccion.objects.filter(estado__in=['en_produccion', 'en_control_qc']).select_related('orden__formula__producto').order_by('-fecha_creacion')
    return render(request, 'produccion/lotes_qc_list.html', {
        'lotes': lotes,
        'titulo': 'Lotes en QC'
    })

@login_required
def orden_list(request):
    """Lista general de órdenes de producción."""
    ordenes = OrdenProduccion.objects.all().select_related('formula__producto').order_by('-id')
    return render(request, 'produccion/orden_list.html', {
        'ordenes': ordenes,
        'titulo': 'Órdenes de Producción'
    })

@login_required
def orden_detail(request, pk):
    """Vista detallada de una orden, consumos y lotes generados."""
    orden = get_object_or_404(OrdenProduccion.objects.select_related('formula__producto'), pk=pk)
    consumos = orden.consumos.all().select_related('materia_prima')
    lotes = orden.lotes.all()
    
    return render(request, 'produccion/orden_detail.html', {
        'orden': orden,
        'consumos': consumos,
        'lotes': lotes,
        'titulo': f'Detalle de Orden OP-{orden.id}'
    })

@login_required
@transaction.atomic
def orden_iniciar(request, pk):
    """
    Cambia el estado de la orden a 'en_proceso' y registra la fecha de inicio.
    En este punto se podrían validar existencias críticas de materia prima.
    """
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    
    if orden.estado != 'planificada':
        messages.warning(request, "La orden no se puede iniciar porque no está en estado planificada.")
        return redirect('produccion:orden_detail', pk=pk)
    
    if request.method == 'POST':
        orden.estado = 'en_proceso'
        orden.fecha_inicio = timezone.now()
        orden.save()
        
        messages.success(request, f"Orden OP-{orden.id} ha sido iniciada. El personal ya puede registrar consumos.")
        return redirect('produccion:orden_detail', pk=pk)
    
    return render(request, 'produccion/orden_confirmar_inicio.html', {'orden': orden})

@login_required
@transaction.atomic
def registrar_consumo_real(request, pk):
    """Permite registrar la cantidad exacta de materia prima utilizada."""
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    
    if orden.estado != 'en_proceso':
        messages.error(request, "Solo se pueden registrar consumos en órdenes en proceso.")
        return redirect('produccion:orden_detail', pk=pk)
        
    if request.method == 'POST':
        materia_id = request.POST.get('materia_prima')
        cantidad = float(request.POST.get('cantidad', 0))
        
        materia = get_object_or_404(MateriaPrima, pk=materia_id)
        
        # Registrar el consumo con el costo unitario actual
        ConsumoMateriaPrima.objects.create(
            orden=orden,
            materia_prima=materia,
            cantidad_consumida=cantidad,
            costo_unitario_al_momento=materia.costo_unitario
        )
        
        # Rebajar stock físico de la materia prima
        materia.stock_actual -= Decimal(cantidad)
        materia.save()
        
        messages.success(request, f"Consumo de {materia.nombre} registrado correctamente.")
        return redirect('produccion:orden_detail', pk=pk)

@login_required
@transaction.atomic
def orden_completar(request, pk):
    """
    Cierra la orden, calcula el costo total real de producción 
    y valida que existan lotes aprobados.
    """
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    
    if orden.estado != 'en_proceso':
        messages.error(request, "Solo se pueden completar órdenes que estén actualmente en proceso.")
        return redirect('produccion:orden_detail', pk=pk)
        
    if request.method == 'POST':
        # Cálculo de costos reales: Suma de (cantidad * costo_unitario) de todos los consumos
        resumen_costo = orden.consumos.aggregate(
            total=Sum(F('cantidad_consumida') * F('costo_unitario_al_momento'))
        )
        
        orden.costo_total_real = resumen_costo['total'] or 0
        orden.estado = 'completada'
        orden.fecha_fin = timezone.now()
        orden.save()
        
        messages.success(request, f"Orden OP-{orden.id} finalizada. Costo total real: ${orden.costo_total_real}")
        return redirect('produccion:orden_detail', pk=pk)

    return render(request, 'produccion/orden_confirmar_cierre.html', {'orden': orden})

@login_required
@transaction.atomic
def control_calidad_create(request, lote_pk):
    """
    Registra los parámetros de control de calidad para un lote específico.
    Actualiza el estado del lote a 'aprobado' o 'rechazado' y la cantidad final producida.
    """
    lote = get_object_or_404(LoteProduccion, pk=lote_pk)

    # No permitir modificar QC si el lote ya fue liberado
    if lote.estado == 'liberado':
        messages.error(request, f"El lote {lote.numero_lote} ya ha sido liberado al almacén y su Control de Calidad no puede ser modificado.")
        return redirect('produccion:orden_detail', pk=lote.orden.pk)

    control_calidad_existente = None
    try:
        control_calidad_existente = ControlCalidad.objects.get(lote=lote)
    except ControlCalidad.DoesNotExist:
        pass

    if request.method == 'POST':
        form = ControlCalidadForm(request.POST, instance=control_calidad_existente, lote_instance=lote)
        if form.is_valid():
            control_calidad = form.save(commit=False)
            control_calidad.lote = lote
            control_calidad.fecha_inspeccion = timezone.now() # Asegurar que la fecha de inspección se actualice
            control_calidad.save() # El método save del formulario también actualiza lote.cantidad_final

            # Actualizar el estado del lote según el resultado del QC
            if control_calidad.aprobado:
                lote.estado = 'aprobado'
                messages.success(request, f"Control de Calidad para lote {lote.numero_lote} registrado y APROBADO. Cantidad final: {lote.cantidad_final}")
            else:
                lote.estado = 'rechazado'
                messages.warning(request, f"Control de Calidad para lote {lote.numero_lote} registrado y RECHAZADO. Cantidad final: {lote.cantidad_final}")
            lote.save(update_fields=['estado']) # Solo actualiza el estado, la cantidad ya fue actualizada por form.save()

            return redirect('produccion:orden_detail', pk=lote.orden.pk)
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario de Control de Calidad.")
    else:
        form = ControlCalidadForm(instance=control_calidad_existente, lote_instance=lote)
    
    context = {
        'form': form,
        'lote': lote,
        'titulo': f'Control de Calidad para Lote {lote.numero_lote}',
        'orden': lote.orden # Para la navegación (breadcrumbs)
    }
    return render(request, 'produccion/control_calidad_form.html', context)

@login_required
@transaction.atomic
def lote_liberar(request, pk):
    """
    Cambia el estado de un LoteProduccion a 'liberado' (al almacén).
    Este cambio disparará la señal para actualizar el stock del ProductoTerminado.
    """
    lote = get_object_or_404(LoteProduccion, pk=pk)

    if lote.estado != 'aprobado':
        messages.error(request, f"El lote {lote.numero_lote} no puede ser liberado al almacén porque no está en estado 'Aprobado'. Estado actual: {lote.get_estado_display()}.")
        return redirect('produccion:orden_detail', pk=lote.orden.pk)
    
    if request.method == 'POST':
        lote.estado = 'liberado'
        lote.save() # Esta acción disparará la señal post_save para actualizar el stock
        messages.success(request, f"Lote {lote.numero_lote} liberado al almacén. Stock de producto terminado actualizado.")
        return redirect('produccion:orden_detail', pk=lote.orden.pk)
    
    context = {
        'lote': lote,
        'titulo': f'Liberar Lote {lote.numero_lote} al Almacén',
        'orden': lote.orden # Para la navegación (breadcrumbs)
    }
    return render(request, 'produccion/lote_confirmar_liberar.html', context)
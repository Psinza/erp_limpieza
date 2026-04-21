from django.shortcuts import render, redirect
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import MovimientoInventario
from apps.produccion.models import MateriaPrima, ProductoTerminado
from .forms import MovimientoInventarioForm

@login_required
def reporte_kardex(request):
    # Obtener parámetros de filtro
    tipo_item = request.GET.get('tipo_item') # 'MP' o 'PT'
    item_id = request.GET.get('item_id')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    movimientos = []
    item = None
    saldo_inicial = 0

    if item_id and tipo_item:
        # Seleccionar el modelo según el tipo
        if tipo_item == 'MP':
            item = MateriaPrima.objects.get(pk=item_id)
            filtro_item = Q(materia_prima=item)
        else:
            item = ProductoTerminado.objects.get(pk=item_id)
            filtro_item = Q(producto_pt=item)

        # 1. Calcular Saldo Inicial (Movimientos anteriores a fecha_desde)
        if fecha_desde:
            movs_previos = MovimientoInventario.objects.filter(filtro_item, fecha__lt=fecha_desde)
            entradas = movs_previos.filter(tipo='E').aggregate(total=Sum('cantidad'))['total'] or 0
            salidas = movs_previos.filter(tipo='S').aggregate(total=Sum('cantidad'))['total'] or 0
            saldo_inicial = entradas - salidas

        # 2. Obtener movimientos en el rango
        qs = MovimientoInventario.objects.filter(filtro_item).order_by('fecha')
        if fecha_desde:
            qs = qs.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__lte=fecha_hasta)
        
        # 3. Construir el Kardex Progresivo
        saldo_progresivo = saldo_inicial
        for m in qs:
            if m.tipo == 'E':
                saldo_progresivo += m.cantidad
            elif m.tipo == 'S':
                saldo_progresivo -= m.cantidad
            
            movimientos.append({
                'fecha': m.fecha,
                'documento': m.documento_referencia,
                'motivo': m.motivo,
                'entrada': m.cantidad if m.tipo == 'E' else 0,
                'salida': m.cantidad if m.tipo == 'S' else 0,
                'saldo': saldo_progresivo,
                'costo': m.costo_unitario
            })

    return render(request, 'logistica/reporte_kardex.html', {
        'movimientos': movimientos,
        'item': item,
        'saldo_inicial': saldo_inicial,
        'materias_primas': MateriaPrima.objects.all(),
        'productos_pt': ProductoTerminado.objects.all(),
    })

@login_required
@transaction.atomic
def registrar_transferencia(request):
    """
    Registra un movimiento de tipo Transferencia ('T'). 
    La validación de origen/destino y stock se maneja en el Formulario.
    """
    if request.method == 'POST':
        form = MovimientoInventarioForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.tipo = 'T'
            movimiento.save()
            messages.success(request, "Transferencia entre almacenes registrada exitosamente.")
            return redirect('logistica:reporte_kardex')
    else:
        form = MovimientoInventarioForm(initial={'tipo': 'T'})
    
    return render(request, 'logistica/transferencia_form.html', {'form': form})
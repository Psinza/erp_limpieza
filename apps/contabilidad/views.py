from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

# ─── Importaciones seguras ──────────────────────────────────────────────────
def _get_models():
    from apps.core.models import EjercicioContable, AsientoContable, CuentaContable, LineaAsiento
    return EjercicioContable, AsientoContable, CuentaContable, LineaAsiento


@login_required
def dashboard(request):
    """Panel principal del módulo de Contabilidad."""
    try:
        EjercicioContable, AsientoContable, CuentaContable, _ = _get_models()
        ejercicio_activo = EjercicioContable.objects.filter(cerrado=False).first()
        total_asientos = AsientoContable.objects.filter(ejercicio=ejercicio_activo).count() if ejercicio_activo else 0
        asientos_pend = AsientoContable.objects.filter(ejercicio=ejercicio_activo, estado='borrador').count() if ejercicio_activo else 0
        total_cuentas = CuentaContable.objects.filter(activo=True).count()
        saldos_tipo = {}
        for tipo, label in CuentaContable.TIPOS_CUENTA:
            saldo = CuentaContable.objects.filter(tipo=tipo, activo=True, es_cuenta_mayor=False).aggregate(total=Sum('saldo_actual'))['total'] or 0
            saldos_tipo[tipo] = {'label': label, 'saldo': float(saldo)}
        ultimos_asientos = AsientoContable.objects.all().order_by('-fecha_creacion')[:5]
    except Exception:
        ejercicio_activo = None
        total_asientos = 0
        asientos_pend = 0
        total_cuentas = 0
        saldos_tipo = {}
        ultimos_asientos = []

    return render(request, 'contabilidad/dashboard_contabilidad.html', {
        'titulo': 'Gestión Contable (NIF-VEN)',
        'total_asientos': total_asientos,
        'asientos_pend': asientos_pend,
        'total_cuentas': total_cuentas,
        'ejercicio_activo': ejercicio_activo,
        'saldos_tipo': saldos_tipo,
        'ultimos_asientos': ultimos_asientos,
    })


@login_required
def asiento_list(request):
    try:
        _, AsientoContable, _, _ = _get_models()
        asientos = AsientoContable.objects.order_by('-fecha_creacion')
    except Exception:
        asientos = []
    return render(request, 'contabilidad/asiento_list.html', {'titulo': 'Libro Diario — Asientos', 'asientos': asientos})

@login_required
def asiento_detail(request, pk):
    _, AsientoContable, _, LineaAsiento = _get_models()
    asiento = get_object_or_404(AsientoContable, pk=pk)
    lineas = asiento.lineas.all()
    from .forms import LineaAsientoForm
    lin_form = LineaAsientoForm()
    return render(request, 'contabilidad/asiento_detail.html', {
        'titulo': f'Asiento {asiento.numero}', 
        'asiento': asiento,
        'lineas': lineas,
        'lin_form': lin_form
    })

@login_required
def asiento_aprobar(request, pk):
    _, AsientoContable, _, _ = _get_models()
    asiento = get_object_or_404(AsientoContable, pk=pk)
    if asiento.estado == 'borrador' and asiento.esta_cuadrado:
        asiento.estado = 'aprobado'
        asiento.aprobado_por = request.user
        asiento.save()
        messages.success(request, f'Asiento {asiento.numero} aprobado.')
    return redirect('contabilidad:asiento_detail', pk=pk)

@login_required
def asiento_anular(request, pk):
    _, AsientoContable, _, _ = _get_models()
    asiento = get_object_or_404(AsientoContable, pk=pk)
    asiento.estado = 'anulado'
    asiento.save()
    messages.warning(request, f'Asiento {asiento.numero} anulado.')
    return redirect('contabilidad:asiento_detail', pk=pk)

@login_required
def asiento_agregar_linea(request, pk):
    _, AsientoContable, _, LineaAsiento = _get_models()
    asiento = get_object_or_404(AsientoContable, pk=pk)
    if request.method == 'POST':
        from .forms import LineaAsientoForm
        form = LineaAsientoForm(request.POST)
        if form.is_valid():
            linea = form.save(commit=False)
            linea.asiento = asiento
            tipo = form.cleaned_data.get('tipo')
            monto = form.cleaned_data.get('monto')
            if tipo == 'debe':
                linea.debe = monto
            else:
                linea.haber = monto
            linea.save()
            messages.success(request, 'Línea agregada.')
    return redirect('contabilidad:asiento_detail', pk=pk)

@login_required
def asiento_eliminar_linea(request, pk, linea_pk):
    _, _, _, LineaAsiento = _get_models()
    linea = get_object_or_404(LineaAsiento, pk=linea_pk, asiento_id=pk)
    if linea.asiento.estado == 'borrador':
        linea.delete()
        messages.info(request, 'Línea eliminada.')
    return redirect('contabilidad:asiento_detail', pk=pk)


from .forms import AsientoContableForm, LineaAsientoFormSet, CuentaContableForm, EjercicioContableForm
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def asiento_create(request):
    EjercicioContable, AsientoContable, _, _ = _get_models()
    if request.method == 'POST':
        form = AsientoContableForm(request.POST)
        formset = LineaAsientoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            asiento = form.save(commit=False)
            asiento.creado_por = request.user
            asiento.save()
            formset.instance = asiento
            formset.save()
            messages.success(request, f'Asiento {asiento.numero} creado exitosamente.')
            return redirect('contabilidad:asiento_list')
    else:
        form = AsientoContableForm()
        formset = LineaAsientoFormSet()
    
    return render(request, 'contabilidad/asiento_form.html', {
        'titulo': 'Nuevo Asiento Contable',
        'form': form,
        'formset': formset
    })

@login_required
def plan_cuentas(request):
    _, _, CuentaContable, _ = _get_models()
    cuentas = CuentaContable.objects.all().order_by('codigo')
    return render(request, 'contabilidad/plan_cuentas.html', {'titulo': 'Plan de Cuentas', 'cuentas': cuentas})

@login_required
def ejercicio_list(request):
    EjercicioContable, _, _, _ = _get_models()
    ejercicios = EjercicioContable.objects.all().order_by('-fecha_inicio')
    return render(request, 'contabilidad/ejercicio_list.html', {'titulo': 'Ejercicios Contables', 'ejercicios': ejercicios})


@login_required
def cuenta_create(request):
    if request.method == 'POST':
        form = CuentaContableForm(request.POST)
        if form.is_valid():
            cuenta = form.save()
            messages.success(request, f'Cuenta {cuenta.codigo} creada exitosamente.')
            return redirect('contabilidad:plan_cuentas')
    else:
        form = CuentaContableForm()
    return render(request, 'contabilidad/cuenta_form.html', {'titulo': 'Nueva Cuenta Contable', 'form': form})

@login_required
def cuenta_update(request, pk):
    _, _, CuentaContable, _ = _get_models()
    cuenta = get_object_or_404(CuentaContable, pk=pk)
    if request.method == 'POST':
        form = CuentaContableForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cuenta {cuenta.codigo} actualizada.')
            return redirect('contabilidad:plan_cuentas')
    else:
        form = CuentaContableForm(instance=cuenta)
    return render(request, 'contabilidad/cuenta_form.html', {'titulo': 'Editar Cuenta', 'form': form})


@login_required
def ejercicio_create(request):
    if request.method == 'POST':
        form = EjercicioContableForm(request.POST)
        if form.is_valid():
            ejercicio = form.save()
            messages.success(request, f'Ejercicio {ejercicio.nombre} creado exitosamente.')
            return redirect('contabilidad:ejercicio_list')
    else:
        form = EjercicioContableForm()
    return render(request, 'contabilidad/ejercicio_form.html', {'titulo': 'Nuevo Ejercicio Contable', 'form': form})

@login_required
def ejercicio_cerrar(request, pk):
    EjercicioContable, _, _, _ = _get_models()
    ejercicio = get_object_or_404(EjercicioContable, pk=pk)
    ejercicio.cerrado = True
    ejercicio.save()
    messages.warning(request, f'Ejercicio {ejercicio.nombre} cerrado.')
    return redirect('contabilidad:ejercicio_list')


@login_required
def libro_diario(request):
    try:
        _, AsientoContable, _, _ = _get_models()
        asientos = AsientoContable.objects.filter(estado='aprobado').order_by('fecha')
    except Exception:
        asientos = []
    return render(request, 'contabilidad/libro_diario.html', {'titulo': 'Libro Diario', 'asientos': asientos})


@login_required
def libro_ventas(request):
    return render(request, 'contabilidad/libro_ventas.html', {'titulo': 'Libro de Ventas'})


@login_required
def balance_general(request):
    try:
        _, _, CuentaContable, _ = _get_models()
        activos = CuentaContable.objects.filter(tipo='activo', activo=True)
        pasivos = CuentaContable.objects.filter(tipo='pasivo', activo=True)
        patrimonio = CuentaContable.objects.filter(tipo='patrimonio', activo=True)
        total_activo = activos.aggregate(t=Sum('saldo_actual'))['t'] or 0
        total_pasivo = pasivos.aggregate(t=Sum('saldo_actual'))['t'] or 0
        total_patrimonio = patrimonio.aggregate(t=Sum('saldo_actual'))['t'] or 0
    except Exception:
        activos = pasivos = patrimonio = []
        total_activo = total_pasivo = total_patrimonio = 0
    return render(request, 'contabilidad/balance_general.html', {
        'titulo': 'Balance General',
        'activos': activos, 'pasivos': pasivos, 'patrimonio': patrimonio,
        'total_activo': total_activo, 'total_pasivo': total_pasivo, 'total_patrimonio': total_patrimonio,
    })


@login_required
def estado_resultados(request):
    try:
        _, _, CuentaContable, _ = _get_models()
        ingresos = CuentaContable.objects.filter(tipo='ingreso', activo=True)
        gastos = CuentaContable.objects.filter(tipo='gasto', activo=True)
        total_ingresos = ingresos.aggregate(t=Sum('saldo_actual'))['t'] or 0
        total_gastos = gastos.aggregate(t=Sum('saldo_actual'))['t'] or 0
    except Exception:
        ingresos = gastos = []
        total_ingresos = total_gastos = 0
    return render(request, 'contabilidad/estado_resultados.html', {
        'titulo': 'Estado de Resultados',
        'ingresos': ingresos, 'gastos': gastos,
        'total_ingresos': total_ingresos, 'total_gastos': total_gastos,
        'utilidad_neta': float(total_ingresos) - float(total_gastos),
    })


@login_required
def balance_comprobacion(request):
    try:
        _, _, CuentaContable, _ = _get_models()
        cuentas = CuentaContable.objects.filter(activo=True, es_cuenta_mayor=False).order_by('codigo')
    except Exception:
        cuentas = []
    return render(request, 'contabilidad/balance_comprobacion.html', {'titulo': 'Balance de Comprobación', 'cuentas': cuentas})


@login_required
def cuenta_mayor(request):
    try:
        _, _, CuentaContable, _ = _get_models()
        cuentas = CuentaContable.objects.filter(activo=True).order_by('codigo')
    except Exception:
        cuentas = []
    return render(request, 'contabilidad/cuenta_mayor.html', {'titulo': 'Cuenta Mayor', 'cuentas': cuentas})
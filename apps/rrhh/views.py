from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Empleado, Departamento, Nomina, Vacacion, Cargo

@login_required
def dashboard(request):
    """Panel principal del módulo de RRHH."""
    total_empleados = Empleado.objects.filter(activo=True).count()
    total_departamentos = Departamento.objects.count()
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    
    # Intento de filtrar nóminas si el modelo tiene campos de fecha adecuados
    try:
        nominas_mes = Nomina.objects.filter(mes=mes_actual, anio=anio_actual).count()
    except:
        nominas_mes = 0
        
    vacaciones_pendientes = Vacacion.objects.filter(estado='PENDIENTE').count()
    empleados_recientes = Empleado.objects.order_by('-fecha_ingreso')[:5]
    distribucion_dpto = []
    for dep in Departamento.objects.all():
        total = Empleado.objects.filter(departamento=dep, activo=True).count()
        if total > 0:
            distribucion_dpto.append({'nombre': dep.nombre, 'total': total})

    return render(request, 'rrhh/dashboard_rrhh.html', {
        'titulo': 'Recursos Humanos',
        'total_empleados': total_empleados,
        'total_departamentos': total_departamentos,
        'nominas_mes': nominas_mes,
        'vacaciones_pendientes': vacaciones_pendientes,
        'empleados_recientes': empleados_recientes,
        'distribucion_dpto': distribucion_dpto,
    })

from .forms import EmpleadoForm, NominaForm, VacacionForm, DepartamentoForm, CargoForm

# --- Empleados ---
@login_required
def empleado_list(request):
    empleados = Empleado.objects.all().order_by('apellidos')
    return render(request, 'rrhh/empleado_list.html', {'empleados': empleados})

@login_required
def empleado_detail(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    return render(request, 'rrhh/empleado_detail.html', {'e': empleado})

@login_required
def empleado_create(request):
    form = EmpleadoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('rrhh:empleado_list')
    return render(request, 'rrhh/empleado_form.html', {'titulo': 'Nuevo Empleado', 'form': form})

@login_required
def empleado_update(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    form = EmpleadoForm(request.POST or None, request.FILES or None, instance=empleado)
    if form.is_valid():
        form.save()
        return redirect('rrhh:empleado_list')
    return render(request, 'rrhh/empleado_form.html', {'titulo': 'Editar Empleado', 'form': form, 'e': empleado})

@login_required
def empleado_delete(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('rrhh:empleado_list')
    return render(request, 'rrhh/empleado_confirm_delete.html', {'e': empleado})

# --- Nóminas ---
@login_required
def nomina_list(request):
    nominas = Nomina.objects.all().order_by('-anio', '-mes')
    return render(request, 'rrhh/nomina_list.html', {'nominas': nominas})

@login_required
def nomina_create(request):
    form = NominaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('rrhh:nomina_list')
    return render(request, 'rrhh/nomina_form.html', {'titulo': 'Nueva Nómina', 'form': form})

@login_required
def nomina_detail(request, pk):
    nomina = get_object_or_404(Nomina, pk=pk)
    detalles = nomina.detalles.all()
    # Si la nómina está en borrador, podríamos pasar un formulario para agregar empleados
    det_form = None
    if nomina.estado == 'borrador':
        # Aquí se podría implementar un inline formset o un formulario simple
        pass
        
    return render(request, 'rrhh/nomina_detail.html', {
        'nom': nomina,
        'detalles': detalles,
        'det_form': det_form,
        'titulo': f'Detalle de Nómina - {nomina.periodo}'
    })

@login_required
def nomina_calcular(request, pk):
    nomina = get_object_or_404(Nomina, pk=pk)
    # Lógica de cálculo (ejemplo simplificado)
    nomina.total_bruto = sum(d.salario_bruto for d in nomina.detalles.all())
    nomina.total_deducciones = sum(d.total_deducciones for d in nomina.detalles.all())
    nomina.total_neto = nomina.total_bruto - nomina.total_deducciones
    nomina.estado = 'calculada'
    nomina.save()
    return redirect('rrhh:nomina_detail', pk=pk)

@login_required
def nomina_calcular(request, pk):
    nomina = get_object_or_404(Nomina, pk=pk)
    if nomina.estado == 'BORRADOR':
        for detalle in nomina.detalles.all():
            detalle.calcular_ley()
        messages.success(request, f"Cálculos de la {nomina} actualizados.")
    return redirect('rrhh:nomina_detail', pk=pk)

@login_required
def nomina_aprobar(request, pk):
    nomina = get_object_or_404(Nomina, pk=pk)
    if nomina.estado == 'BORRADOR':
        nomina.estado = 'PROCESADA'
        nomina.save()
        messages.success(request, f"La {nomina} ha sido aprobada y procesada.")
    return redirect('rrhh:nomina_detail', pk=pk)

@login_required
def nomina_pagar(request, pk):
    nomina = get_object_or_404(Nomina, pk=pk)
    if nomina.estado == 'PROCESADA':
        nomina.estado = 'PAGADA'
        nomina.save()
        messages.success(request, f"La {nomina} ha sido marcada como PAGADA.")
    return redirect('rrhh:nomina_detail', pk=pk)

@login_required
def nomina_agregar_empleado(request, pk):
    nomina = get_object_or_404(Nomina, pk=pk)
    if request.method == 'POST':
        empleado_id = request.POST.get('empleado')
        if empleado_id:
            from .models import Empleado, NominaDetalle
            empleado = get_object_or_404(Empleado, pk=empleado_id)
            if not NominaDetalle.objects.filter(nomina=nomina, empleado=empleado).exists():
                detalle = NominaDetalle.objects.create(
                    nomina=nomina,
                    empleado=empleado,
                    sueldo_base=empleado.salario_base / 2 if nomina.tipo in ['Q1', 'Q2'] else empleado.salario_base,
                    bono_alimentacion=empleado.bono_alimentacion
                )
                detalle.calcular_ley()
                messages.success(request, f"{empleado.nombre_completo} agregado a la nómina.")
            else:
                messages.warning(request, "El empleado ya está en esta nómina.")
    return redirect('rrhh:nomina_detail', pk=pk)

@login_required
def recibo_pdf(request, pk):
    """Placeholder para generación de PDF de recibo de pago."""
    from .models import NominaDetalle
    detalle = get_object_or_404(NominaDetalle, pk=pk)
    return render(request, 'rrhh/recibo_pdf.html', {
        'detalle': detalle,
        'titulo': f'Recibo de Pago - {detalle.empleado.cedula}'
    })

# --- Vacaciones ---
@login_required
def vacacion_list(request):
    vacaciones = Vacacion.objects.all().order_by('-fecha_inicio')
    return render(request, 'rrhh/vacacion_list.html', {'vacaciones': vacaciones})

@login_required
def vacacion_create(request):
    form = VacacionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('rrhh:vacacion_list')
    return render(request, 'rrhh/vacacion_form.html', {'titulo': 'Nueva Solicitud de Vacaciones', 'form': form})

# --- Estructura ---
@login_required
def departamento_list(request):
    departamentos = Departamento.objects.all()
    return render(request, 'rrhh/departamento_list.html', {'departamentos': departamentos})

@login_required
def departamento_create(request):
    form = DepartamentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('rrhh:departamento_list')
    return render(request, 'rrhh/departamento_form.html', {'titulo': 'Nuevo Departamento', 'form': form})

@login_required
def departamento_update(request, pk):
    dep = get_object_or_404(Departamento, pk=pk)
    form = DepartamentoForm(request.POST or None, instance=dep)
    if form.is_valid():
        form.save()
        return redirect('rrhh:departamento_list')
    return render(request, 'rrhh/departamento_form.html', {'titulo': 'Editar Departamento', 'form': form})

@login_required
def cargo_list(request):
    cargos = Cargo.objects.all()
    return render(request, 'rrhh/cargo_list.html', {'cargos': cargos})

@login_required
def cargo_create(request):
    form = CargoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('rrhh:cargo_list')
    return render(request, 'rrhh/cargo_form.html', {'titulo': 'Nuevo Cargo', 'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Vehiculo, Conductor, Despacho
from .forms import VehiculoForm, DespachoForm, ConductorForm, DespachoFinalizarForm, EntregaDespachoForm
from apps.core.decorators import permiso_requerido

@login_required
@permiso_requerido('TRANSPORTE', 'ver')
def vehiculo_lista(request):
    vehiculos = Vehiculo.objects.select_related('tipo').all()
    return render(request, 'transportes/vehiculo_list.html', {'vehiculos': vehiculos})

@login_required
@permiso_requerido('TRANSPORTE', 'ver')
def vehiculo_detalle(request, pk):
    vehiculo = get_object_or_404(Vehiculo.objects.select_related('tipo'), pk=pk)
    despachos = vehiculo.despachos.all().select_related('ruta', 'conductor').order_by('-fecha_salida')
    mantenimientos = vehiculo.mantenimientos.all().order_by('-fecha_programada')
    return render(request, 'transportes/vehiculo_detail.html', {
        'vehiculo': vehiculo,
        'despachos': despachos,
        'mantenimientos': mantenimientos,
    })

@login_required
@permiso_requerido('TRANSPORTE', 'ver')
def dashboard_transportes(request):
    stats = {
        'total_vehiculos': Vehiculo.objects.count(),
        'en_ruta': Vehiculo.objects.filter(estado='en_ruta').count(),
        'mantenimiento': Vehiculo.objects.filter(estado='mantenimiento').count(),
        'conductores_activos': Conductor.objects.filter(estado='activo').count(),
        'despachos_hoy': Despacho.objects.filter(fecha_salida__date=timezone.now().date()).count(),
    }
    return render(request, 'transportes/dashboard_transportes.html', {'stats': stats})

@login_required
@permiso_requerido('TRANSPORTE', 'crear')
def vehiculo_crear(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehículo registrado correctamente.")
            return redirect('transportes:vehiculo_lista')
    else:
        form = VehiculoForm()
    return render(request, 'transportes/vehiculo_form.html', {'form': form, 'titulo': 'Registrar Vehículo'})

@login_required
@permiso_requerido('TRANSPORTE', 'crear')
def despacho_crear(request):
    if request.method == 'POST':
        form = DespachoForm(request.POST)
        if form.is_valid():
            despacho = form.save(commit=False)
            despacho.numero = Despacho.generar_numero()
            despacho.creado_por = request.user
            despacho.save()
            
            # Actualizar estado del vehículo
            despacho.vehiculo.estado = 'en_ruta'
            despacho.vehiculo.save()
            
            messages.success(request, f"Despacho {despacho.numero} programado con éxito.")
            return redirect('transportes:dashboard')
    else:
        form = DespachoForm()
    return render(request, 'transportes/despacho_form.html', {'form': form})

@login_required
@permiso_requerido('TRANSPORTE', 'editar')
def despacho_detalle(request, pk):
    despacho = get_object_or_404(Despacho.objects.select_related('vehiculo', 'conductor', 'ruta'), pk=pk)
    entregas = despacho.entregas.all().select_related('punto_entrega')
    return render(request, 'transportes/despacho_detail.html', {
        'despacho': despacho,
        'entregas': entregas
    })

@login_required
@permiso_requerido('TRANSPORTE', 'editar')
def despacho_finalizar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        form = DespachoFinalizarForm(request.POST, instance=despacho)
        if form.is_valid():
            despacho = form.save(commit=False)
            despacho.estado = 'completado'
            despacho.km_recorridos = despacho.odometro_llegada - despacho.odometro_salida
            despacho.save()
            
            # Liberar vehículo
            despacho.vehiculo.estado = 'disponible'
            despacho.vehiculo.odometro = despacho.odometro_llegada
            despacho.vehiculo.save()
            
            messages.success(request, f"Despacho {despacho.numero} finalizado correctamente.")
            return redirect('transportes:despacho_list')
    else:
        form = DespachoFinalizarForm(instance=despacho)
    return render(request, 'transportes/despacho_finish.html', {'form': form, 'despacho': despacho})

@login_required
@permiso_requerido('TRANSPORTE', 'ver')
def conductor_lista(request):
    conductores = Conductor.objects.all()
    return render(request, 'transportes/conductor_list.html', {'conductores': conductores})

@login_required
@permiso_requerido('TRANSPORTE', 'ver')
def despacho_lista(request):
    despachos = Despacho.objects.select_related('vehiculo', 'conductor', 'ruta').all().order_by('-fecha_salida')
    return render(request, 'transportes/despacho_list.html', {'despachos': despachos})

@login_required
@permiso_requerido('TRANSPORTE', 'crear')
def conductor_crear(request):
    if request.method == 'POST':
        form = ConductorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Conductor registrado correctamente.")
            return redirect('transportes:conductor_list')
    else:
        form = ConductorForm()
    return render(request, 'transportes/conductor_form.html', {'form': form, 'titulo': 'Registrar Conductor'})

@login_required
@permiso_requerido('TRANSPORTE', 'ver')
def conductor_detalle(request, pk):
    conductor = get_object_or_404(Conductor, pk=pk)
    despachos = conductor.despachos.all().select_related('vehiculo', 'ruta').order_by('-fecha_salida')
    return render(request, 'transportes/conductor_detail.html', {
        'conductor': conductor,
        'despachos': despachos
    })

@login_required
@permiso_requerido('TRANSPORTE', 'editar')
def conductor_editar(request, pk):
    conductor = get_object_or_404(Conductor, pk=pk)
    if request.method == 'POST':
        form = ConductorForm(request.POST, request.FILES, instance=conductor)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos del conductor actualizados.")
            return redirect('transportes:conductor_list')
    else:
        form = ConductorForm(instance=conductor)
    return render(request, 'transportes/conductor_form.html', {'form': form, 'titulo': 'Editar Conductor'})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from .models import SolicitudViatico, GastoViatico
from .forms import SolicitudViaticoForm, GastoViaticoForm

@login_required
def dashboard_viaticos(request):
    """Dashboard de viáticos."""
    if request.user.is_staff:
        solicitudes = SolicitudViatico.objects.select_related('solicitante').all()[:10]
    else:
        solicitudes = SolicitudViatico.objects.filter(solicitante=request.user)[:10]
    
    context = {
        'solicitudes': solicitudes,
    }
    return render(request, 'viaticos/dashboard.html', context)

@login_required
def solicitud_list(request):
    if request.user.is_staff:
        solicitudes = SolicitudViatico.objects.select_related('solicitante').all()
    else:
        solicitudes = SolicitudViatico.objects.filter(solicitante=request.user)
    return render(request, 'viaticos/solicitud_list.html', {'solicitudes': solicitudes})

@login_required
def solicitud_create(request):
    if request.method == 'POST':
        form = SolicitudViaticoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = request.user
            solicitud.save()
            messages.success(request, 'Solicitud de viático creada exitosamente.')
            return redirect('viaticos:solicitud_detail', pk=solicitud.pk)
    else:
        form = SolicitudViaticoForm()
    return render(request, 'viaticos/solicitud_form.html', {'form': form, 'title': 'Crear Solicitud de Viático'})

@login_required
def solicitud_detail(request, pk):
    solicitud = get_object_or_404(SolicitudViatico, pk=pk)
    gastos = solicitud.gastos.all()
    
    # Solo el solicitante o staff pueden ver
    if not request.user.is_staff and solicitud.solicitante != request.user:
        messages.error(request, 'No tienes permiso para ver esta solicitud.')
        return redirect('viaticos:dashboard')
    
    return render(request, 'viaticos/solicitud_detail.html', {'solicitud': solicitud, 'gastos': gastos})

@login_required
def solicitud_aprobar(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para aprobar solicitudes.')
        return redirect('viaticos:dashboard')
    
    solicitud = get_object_or_404(SolicitudViatico, pk=pk)
    if solicitud.estado == 'pendiente':
        solicitud.estado = 'aprobada'
        solicitud.aprobado_por = request.user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.save()
        messages.success(request, 'Solicitud aprobada exitosamente.')
    return redirect('viaticos:solicitud_detail', pk=pk)

@login_required
def gasto_create(request, solicitud_pk):
    solicitud = get_object_or_404(SolicitudViatico, pk=solicitud_pk)
    
    # Solo el solicitante puede agregar gastos
    if solicitud.solicitante != request.user:
        messages.error(request, 'No tienes permiso para agregar gastos a esta solicitud.')
        return redirect('viaticos:dashboard')
    
    if request.method == 'POST':
        form = GastoViaticoForm(request.POST, request.FILES)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.solicitud = solicitud
            gasto.save()
            messages.success(request, 'Gasto agregado exitosamente.')
            return redirect('viaticos:solicitud_detail', pk=solicitud_pk)
    else:
        form = GastoViaticoForm()
    return render(request, 'viaticos/gasto_form.html', {'form': form, 'solicitud': solicitud, 'title': 'Agregar Gasto'})
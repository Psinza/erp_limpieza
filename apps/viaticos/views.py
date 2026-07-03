from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudViatico
from .forms import SolicitudViaticoForm, GastoViaticoForm

@login_required
def dashboard(request):
    solicitudes = SolicitudViatico.objects.all().order_by('-fecha_solicitud')
    return render(request, 'viaticos/dashboard.html', {
        'titulo': 'Gestión de Viáticos',
        'solicitudes': solicitudes
    })

@login_required
def solicitud_create(request):
    if request.method == 'POST':
        form = SolicitudViaticoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.creado_por = request.user
            solicitud.save()
            messages.success(request, 'Solicitud de viático creada exitosamente.')
            return redirect('viaticos:dashboard')
    else:
        form = SolicitudViaticoForm()
    return render(request, 'viaticos/solicitud_form.html', {
        'form': form,
        'titulo': 'Nueva Solicitud de Viático'
    })

@login_required
def solicitud_update(request, pk):
    solicitud = get_object_or_404(SolicitudViatico, pk=pk)
    if request.method == 'POST':
        form = SolicitudViaticoForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitud actualizada exitosamente.')
            return redirect('viaticos:dashboard')
    else:
        form = SolicitudViaticoForm(instance=solicitud)
    return render(request, 'viaticos/solicitud_form.html', {
        'form': form,
        'titulo': 'Editar Solicitud'
    })

@login_required
def solicitud_delete(request, pk):
    solicitud = get_object_or_404(SolicitudViatico, pk=pk)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'Solicitud eliminada.')
        return redirect('viaticos:dashboard')
    return render(request, 'core/confirm_delete.html', {'objeto': solicitud})
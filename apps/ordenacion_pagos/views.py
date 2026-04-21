from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudPago
from .forms import SolicitudPagoForm

@login_required
def dashboard_ordenacion(request):
    """Panel para revisión y aprobación de pagos."""
    solicitudes = SolicitudPago.objects.all().order_by('-fecha_solicitud')
    
    context = {
        'solicitudes': solicitudes,
        'pendientes': solicitudes.filter(estado='pendiente').count(),
        'autorizados': solicitudes.filter(estado='autorizado').count(),
    }
    return render(request, 'ordenacion_pagos/dashboard.html', context)

@login_required
def solicitud_create(request):
    if request.method == 'POST':
        form = SolicitudPagoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitud de pago creada exitosamente.')
            return redirect('ordenacion_pagos:dashboard')
    else:
        form = SolicitudPagoForm()
    return render(request, 'ordenacion_pagos/solicitud_form.html', {'form': form, 'title': 'Crear Solicitud de Pago'})

@login_required
def autorizar_pago(request, pk):
    """Cambia el estado de una solicitud de pago."""
    if request.method != 'POST':
        return redirect('ordenacion_pagos:dashboard')
        
    solicitud = get_object_or_404(SolicitudPago, pk=pk)
    nuevo_estado = request.POST.get('estado')
    
    if solicitud.estado != 'pendiente':
        messages.warning(request, "Esta solicitud ya ha sido procesada previamente.")
        return redirect('ordenacion_pagos:dashboard')

    if nuevo_estado in ['autorizado', 'rechazado']:
        solicitud.estado = nuevo_estado
        solicitud.autorizado_por = request.user
        solicitud.notas_auditoria = request.POST.get('notas', '')
        solicitud.save()
        
        messages.success(request, f"Solicitud de pago ha sido {nuevo_estado}.")
    
    return redirect('ordenacion_pagos:dashboard')

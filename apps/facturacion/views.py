from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import Cliente, Factura, ItemFactura, NotaEntrega, Presupuesto, ItemPresupuesto
from .forms import ClienteForm, FacturaForm, ItemFacturaForm, NotaEntregaForm, PresupuestoForm, ItemPresupuestoForm

@login_required
def dashboard_facturacion(request):
    """Dashboard de facturación."""
    facturas = Factura.objects.select_related('cliente').all()[:10]
    presupuestos = Presupuesto.objects.select_related('cliente').filter(estado='borrador')[:5]
    
    context = {
        'facturas': facturas,
        'presupuestos': presupuestos,
    }
    return render(request, 'facturacion/dashboard.html', context)

# Clientes
@login_required
def cliente_list(request):
    clientes = Cliente.objects.all()
    return render(request, 'facturacion/cliente_list.html', {'clientes': clientes})

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('facturacion:cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'facturacion/cliente_form.html', {'form': form, 'title': 'Crear Cliente'})

@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('facturacion:cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'facturacion/cliente_form.html', {'form': form, 'title': 'Editar Cliente'})

# Facturas
@login_required
def factura_list(request):
    facturas = Factura.objects.select_related('cliente').all()
    return render(request, 'facturacion/factura_list.html', {'facturas': facturas})

@login_required
def factura_create(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.creado_por = request.user
            factura.save()
            messages.success(request, 'Factura creada exitosamente.')
            return redirect('facturacion:factura_detail', pk=factura.pk)
    else:
        form = FacturaForm()
    return render(request, 'facturacion/factura_form.html', {'form': form, 'title': 'Crear Factura'})

@login_required
def factura_detail(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    items = factura.items.all()
    return render(request, 'facturacion/factura_detail.html', {'factura': factura, 'items': items})

@login_required
def factura_pdf(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"Factura N°: {factura.numero}")
    p.drawString(100, 730, f"Cliente: {factura.cliente.nombre}")
    p.drawString(100, 710, f"Fecha: {factura.fecha_emision}")
    p.drawString(100, 690, f"Total: {factura.total}")
    p.showPage()
    p.save()
    
    return response

# Nota de Entrega
@login_required
def nota_entrega_list(request):
    notas = NotaEntrega.objects.select_related('cliente').all()
    return render(request, 'facturacion/nota_entrega_list.html', {'notas': notas})

@login_required
def nota_entrega_create(request):
    if request.method == 'POST':
        form = NotaEntregaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.creado_por = request.user
            nota.save()
            messages.success(request, 'Nota de entrega creada exitosamente.')
            return redirect('facturacion:nota_entrega_list')
    else:
        form = NotaEntregaForm()
    return render(request, 'facturacion/nota_entrega_form.html', {'form': form, 'title': 'Crear Nota de Entrega'})

# Presupuestos
@login_required
def presupuesto_list(request):
    presupuestos = Presupuesto.objects.select_related('cliente').all()
    return render(request, 'facturacion/presupuesto_list.html', {'presupuestos': presupuestos})

@login_required
def presupuesto_create(request):
    if request.method == 'POST':
        form = PresupuestoForm(request.POST)
        if form.is_valid():
            presupuesto = form.save(commit=False)
            presupuesto.creado_por = request.user
            presupuesto.save()
            messages.success(request, 'Presupuesto creado exitosamente.')
            return redirect('facturacion:presupuesto_detail', pk=presupuesto.pk)
    else:
        form = PresupuestoForm()
    return render(request, 'facturacion/presupuesto_form.html', {'form': form, 'title': 'Crear Presupuesto'})

@login_required
def presupuesto_detail(request, pk):
    presupuesto = get_object_or_404(Presupuesto, pk=pk)
    items = presupuesto.items.all()
    return render(request, 'facturacion/presupuesto_detail.html', {'presupuesto': presupuesto, 'items': items})
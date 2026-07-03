from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.facturacion.models import Proveedor
from apps.produccion.models import MateriaPrima
from .models import ProductoCompra
from .forms import ProveedorForm, MateriaPrimaForm, ProductoCompraForm

@login_required
def dashboard(request):
    """Panel principal del módulo de Compras."""
    stats = {
        'ordenes_pendientes': 4,
        'compras_mes': 9420.00,
    }
    return render(request, 'compras/dashboard.html', {'titulo': 'Gestión de Compras', 'stats': stats})

# --- PROVEEDORES ---
@login_required
def proveedor_list(request):
    proveedores = Proveedor.objects.all().order_by('razon_social')
    return render(request, 'compras/proveedor_list.html', {'proveedores': proveedores, 'titulo': 'Proveedores'})

@login_required
def proveedor_create(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compras:proveedor_list')
    else:
        form = ProveedorForm()
    return render(request, 'compras/proveedor_form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})

@login_required
def proveedor_update(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('compras:proveedor_list')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'compras/proveedor_form.html', {'form': form, 'titulo': 'Editar Proveedor'})

# --- MATERIAS PRIMAS ---
@login_required
def materia_prima_list(request):
    materias = MateriaPrima.objects.all().order_by('nombre')
    return render(request, 'compras/materia_prima_list.html', {'materias': materias, 'titulo': 'Materias Primas'})

@login_required
def materia_prima_create(request):
    if request.method == 'POST':
        form = MateriaPrimaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compras:materia_prima_list')
    else:
        form = MateriaPrimaForm()
    return render(request, 'compras/materia_prima_form.html', {'form': form, 'titulo': 'Nueva Materia Prima'})

@login_required
def materia_prima_update(request, pk):
    materia = get_object_or_404(MateriaPrima, pk=pk)
    if request.method == 'POST':
        form = MateriaPrimaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            return redirect('compras:materia_prima_list')
    else:
        form = MateriaPrimaForm(instance=materia)
    return render(request, 'compras/materia_prima_form.html', {'form': form, 'titulo': 'Editar Materia Prima'})

# --- PRODUCTOS DE COMPRA ---
@login_required
def producto_list(request):
    productos = ProductoCompra.objects.all().order_by('nombre')
    return render(request, 'compras/producto_list.html', {'productos': productos, 'titulo': 'Productos de Compra'})

@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoCompraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('compras:producto_list')
    else:
        form = ProductoCompraForm()
    return render(request, 'compras/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto de Compra'})

@login_required
def producto_update(request, pk):
    producto = get_object_or_404(ProductoCompra, pk=pk)
    if request.method == 'POST':
        form = ProductoCompraForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('compras:producto_list')
    else:
        form = ProductoCompraForm(instance=producto)
    return render(request, 'compras/producto_form.html', {'form': form, 'titulo': 'Editar Producto de Compra'})
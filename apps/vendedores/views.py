from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_vendedores(request):
    """Panel principal del módulo de Vendedores."""
    return render(request, 'vendedores/dashboard.html', {'titulo': 'Gestión de Vendedores'})

@login_required
def vendedor_list(request):
    """Lista de todos los vendedores registrados."""
    return render(request, 'vendedores/vendedor_list.html', {'titulo': 'Lista de Vendedores'})

@login_required
def vendedor_create(request):
    """Formulario para registrar un nuevo vendedor."""
    return render(request, 'vendedores/vendedor_form.html', {'titulo': 'Nuevo Vendedor'})

@login_required
def vendedor_edit(request, pk):
    """Formulario para editar un vendedor existente."""
    return render(request, 'vendedores/vendedor_form.html', {'titulo': 'Editar Vendedor'})

@login_required
def comision_list(request):
    """Lista de comisiones de vendedores."""
    return render(request, 'vendedores/comision_list.html', {'titulo': 'Comisiones'})

@login_required
def comision_create(request):
    """Crea una nueva comisión (Función requerida por urls.py)."""
    return render(request, 'vendedores/comision_form.html', {'titulo': 'Nueva Comisión'})
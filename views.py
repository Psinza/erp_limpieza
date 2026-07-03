from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Control de flujo de efectivo y disponibilidades."""
    context = {
        'titulo': 'Tesorería y Finanzas',
        'disponible_bancos': 0.0,
        'disponible_caja': 0.0,
    }
    return render(request, 'tesoreria/dashboard.html', context)

@login_required
def caja_list(request):
    """Movimientos de caja chica y principal."""
    return render(request, 'tesoreria/caja_list.html')

@login_required
def banco_list(request):
    """Gestión de cuentas bancarias y conciliación."""
    return render(request, 'tesoreria/banco_list.html')

@login_required
def pago_list(request):
    """Registro de egresos y pagos a proveedores."""
    return render(request, 'tesoreria/pago_list.html')
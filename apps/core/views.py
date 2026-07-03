from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.urls import NoReverseMatch
from django.contrib import messages
from .models import Usuario, Area, Empresa
from .forms import EmpresaForm

@login_required
def dashboard_principal(request):
    """Dashboard principal con gestión de errores de URL y módulos agrupados."""
    modulos_raw = [ 
        {'nombre': 'Comercialización', 'icono': 'bi-cart4', 'url': 'comercializacion:dashboard', 'color': 'primary', 'desc': 'Coordinación de Ventas, Compras y Pedidos', 'cat': 'Operaciones'},
        {'nombre': 'Ventas', 'icono': 'bi-cash-stack', 'url': 'ventas:dashboard', 'color': 'success', 'desc': 'Facturación y Clientes', 'cat': 'Operaciones'},
        {'nombre': 'Compras', 'icono': 'bi-bag-check', 'url': 'compras:dashboard', 'color': 'warning', 'desc': 'Proveedores y Órdenes', 'cat': 'Operaciones'},
        {'nombre': 'Producción', 'icono': 'bi-gear-wide-connected', 'url': 'produccion:dashboard', 'color': 'danger', 'desc': 'Manufactura y Órdenes', 'cat': 'Operaciones'},
        {'nombre': 'Contabilidad', 'icono': 'bi-calculator', 'url': 'contabilidad:dashboard', 'color': 'info', 'desc': 'Libros y Asientos', 'cat': 'Finanzas'},
        {'nombre': 'Facturación', 'icono': 'bi-receipt', 'url': 'facturacion:dashboard', 'color': 'primary', 'desc': 'Documentos Fiscales', 'cat': 'Finanzas'},
        {'nombre': 'Tesorería', 'icono': 'bi-cash-coin', 'url': 'tesoreria:dashboard', 'color': 'success', 'desc': 'Caja y Bancos', 'cat': 'Finanzas'},
        {'nombre': 'Vendedores', 'icono': 'bi-people', 'url': 'vendedores:dashboard', 'color': 'warning', 'desc': 'Gestión de Ventas', 'cat': 'Operaciones'},
        {'nombre': 'Transportes', 'icono': 'bi-truck', 'url': 'transportes:dashboard', 'color': 'info', 'desc': 'Flota y Despachos', 'cat': 'Operaciones'},
        {'nombre': 'RRHH', 'icono': 'bi-person-badge', 'url': 'rrhh:dashboard', 'color': 'danger', 'desc': 'Personal y Nómina', 'cat': 'Administración'},
        {'nombre': 'Logística', 'icono': 'bi-box-seam', 'url': 'logistica:dashboard', 'color': 'secondary', 'desc': 'Inventario y Almacén', 'cat': 'Operaciones'},
        {'nombre': 'Mantenimiento', 'icono': 'bi-tools', 'url': 'core:mantenimiento', 'color': 'dark', 'desc': 'Configuración de Empresa', 'cat': 'Configuración'},
    ]

    modulos_agrupados = {}
    for m in modulos_raw:
        try:
            # Intentamos resolver la URL. Si falla, el módulo se marca como inactivo.
            m['url_actual'] = reverse(m['url']) if ':' in m['url'] else '#'
            m['activo'] = True
        except (NoReverseMatch, AttributeError):
            m['url_actual'] = "#"
            m['activo'] = False
            m['desc'] = "[Configuración Pendiente]"

        cat = m.get('cat', 'Otros')
        if cat not in modulos_agrupados:
            modulos_agrupados[cat] = []
        modulos_agrupados[cat].append(m)

    # Métricas para el dashboard
    stats = {
        'total_usuarios': Usuario.objects.filter(activo=True).count(),
        'fecha_servidor': timezone.now(),
        'actividad_hoy': 5, # Placeholder para lógica de logs
    }

    context = {
        'modulos_agrupados': modulos_agrupados,
        'stats': stats,
        'now': timezone.now(),
        'ultimos_logs': [],
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def mantenimiento_empresa(request):
    """Vista para configurar los datos de la empresa y el logo (Solo Superusuarios)."""
    empresa = Empresa.objects.first()
    if not empresa:
        # Crea el registro inicial si no existe
        empresa = Empresa.objects.create(nombre="Configurar Empresa", rif="J-00000000-0")

    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada exitosamente.")
            return redirect('core:dashboard')
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, 'core/mantenimiento.html', {
        'form': form,
        'titulo': 'Mantenimiento del Sistema'
    })

@login_required
def modulo_en_construccion(request, nombre_modulo="Módulo"):
    """Vista genérica para módulos o funciones que aún no han sido implementados."""
    return render(request, 'core/en_construccion.html', {
        'nombre_modulo': nombre_modulo,
        'titulo': f"{nombre_modulo} - En Desarrollo"
    })
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    """Vista principal del ERP con métricas globales y accesos rápidos."""
    hoy = timezone.now().date()
    
    # Métricas robustas
    try:
        total_usuarios = User.objects.filter(is_active=True).count()
        actividad_hoy = 0  # Placeholder
    except Exception:
        total_usuarios = 0
        actividad_hoy = 0

    stats = {
        'total_usuarios': total_usuarios,
        'actividad_hoy': actividad_hoy,
    }
    
    # Módulos del sistema con sus respectivas rutas y estéticas
    modulos = [
        {'nombre': 'RRHH', 'icono': 'bi-people', 'url': 'rrhh:dashboard', 'color': 'primary', 'desc': 'Personal y Nómina'},
        {'nombre': 'Compras', 'icono': 'bi-cart', 'url': 'compras:dashboard', 'color': 'success', 'desc': 'Proveedores e Insumos'},
        {'nombre': 'Ventas', 'icono': 'bi-graph-up', 'url': 'ventas:dashboard', 'color': 'info', 'desc': 'Facturación y Clientes'},
        {'nombre': 'Producción', 'icono': 'bi-gear', 'url': 'produccion:dashboard', 'color': 'secondary', 'desc': 'Fórmulas y Lotes'},
        {'nombre': 'Logística', 'icono': 'bi-box-seam', 'url': 'logistica:reporte_kardex', 'color': 'warning', 'desc': 'Inventarios y Stock'},
        {'nombre': 'Contabilidad', 'icono': 'bi-calculator', 'url': 'contabilidad:dashboard', 'color': 'primary', 'desc': 'Libros y Balances'},
        {'nombre': 'Facturación', 'icono': 'bi-receipt', 'url': 'facturacion:dashboard', 'color': 'dark', 'desc': 'Ventas y Documentos'},
        {'nombre': 'Activos Fijos', 'icono': 'bi-building', 'url': 'activos_fijos:activo_list', 'color': 'info', 'desc': 'Maquinaria y Bienes'},
        {'nombre': 'Viáticos', 'icono': 'bi-briefcase', 'url': 'viaticos:dashboard', 'color': 'warning', 'desc': 'Gastos de Viaje'},
        {'nombre': 'Mantenimiento', 'icono': 'bi-shield-lock', 'url': 'administracion:mantenimiento', 'color': 'danger', 'desc': 'Soporte y Backup'},
    ]

    # Auditoría reciente
    ultimos_logs = []  # Placeholder

    # Datos para el gráfico de ventas (Ejemplo: Últimos 6 meses)
    chart_labels = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
    chart_sales_data = [1200, 1900, 3000, 5000, 2300, 3400]

    context = {
        'stats': stats,
        'modulos': modulos,
        'ultimos_logs': ultimos_logs,
        'now': timezone.now(),
        'chart_labels': chart_labels,
        'chart_sales_data': chart_sales_data,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def perfil(request):
    return render(request, 'core/perfil.html')

@login_required
def modulo_en_construccion(request, nombre_modulo):
    """Vista genérica para módulos que aún no tienen contenido."""
    return render(request, 'core/under_construction.html', {'modulo': nombre_modulo})
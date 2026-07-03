from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import F
from .models import Cliente, ProductoVenta  # Asegúrate de tener estos modelos definidos
from apps.produccion.models import ProductoTerminado

def render_to_pdf(template_src, context_dict={}):
    """Utilidad para generar PDF desde HTML."""
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

@login_required
def dashboard(request):
    """Dashboard específico de Ventas."""
    context = {
        'titulo': 'Gestión de Ventas',
        'clientes_count': Cliente.objects.count(),
    }
    return render(request, 'ventas/dashboard.html', context)

@login_required
def cliente_list(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'ventas/cliente_list.html', {'clientes': clientes})

@login_required
def exportar_clientes_pdf(request):
    """Genera el reporte PDF de clientes."""
    clientes = Cliente.objects.all().order_by('nombre')
    data = {
        'clientes': clientes,
        'titulo': 'Reporte Maestro de Clientes'
    }
    return render_to_pdf('ventas/clientes_list_pdf.html', data)

@login_required
def disponibilidad_productos(request):
    """
    Cruza ProductoVenta con ProductoTerminado para ver stock real.
    """
    stock_minimo = request.GET.get('stock_minimo')
    productos = ProductoVenta.objects.select_related('producto_base').all()

    if stock_minimo:
        try:
            min_val = float(stock_minimo)
            productos = productos.filter(producto_base__stock_actual__lte=min_val)
        except ValueError:
            pass

    return render(request, 'ventas/disponibilidad.html', {
        'productos': productos,
        'stock_minimo_filtro': stock_minimo,
    })

def cliente_create(request): pass # Implementar según tus formularios
def producto_list(request): pass # Implementar lista de precios

def pedido_list(request):
    pass


def pedido_list(request):
    pass

def pedido_create(request):
    pass


def cotizacion_list(request):
    pass

def cotizacion_create(request):
    pass

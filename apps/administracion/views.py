import io
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import ConfiguracionEmpresa
from .forms import ConfiguracionEmpresaForm, UserForm
from .utils import realizar_backup_postgresql

@login_required
def mantenimiento_sistema(request):
    """Panel de control para backups y logs."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado.")
        return redirect('core:dashboard')
    
    if 'backup' in request.POST:
        path, error = realizar_backup_postgresql()
        if path:
            messages.success(request, f"Respaldo creado exitosamente: {path}")
        else:
            messages.error(request, f"Error en respaldo: {error}")

    logs = LogAuditoria.objects.all().order_by('-fecha')[:50]
    return render(request, 'administracion/mantenimiento.html', {'logs': logs})
    context = {
        'ultimas_facturas': Factura.objects.all().order_by('-fecha')[:5],
        'presupuestos_pendientes': Presupuesto.objects.filter(estado='pendiente').count(),
    }
    return render(request, 'facturacion/dashboard.html', context)

def _generar_factura_pdf_buffer(factura):
    """Función auxiliar interna para generar el contenido del PDF en un buffer."""
    detalles = factura.detalles.all()
    
    # Intentar obtener configuración de la base de datos
    config_obj = ConfiguracionEmpresa.objects.first()

    nombre_empresa = config_obj.nombre if config_obj else settings.ERP_CONFIG.get('EMPRESA_NOMBRE')
    ruc_empresa = config_obj.ruc if config_obj else settings.ERP_CONFIG.get('EMPRESA_RUC')
    telf_empresa = config_obj.telefono if config_obj else settings.ERP_CONFIG.get('EMPRESA_TELEFONO')
    ciudad_empresa = config_obj.ciudad if config_obj else settings.ERP_CONFIG.get('EMPRESA_CIUDAD')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Dibujar Logo si existe
    if config_obj and config_obj.logo:
        try:
            p.drawImage(config_obj.logo.path, 50, height - 80, width=60, height=60, preserveAspectRatio=True)
        except:
            pass

    # Cabecera - Datos de la Empresa
    p.setFont("Helvetica-Bold", 16)
    p.drawString(120 if config_obj and config_obj.logo else 50, height - 50, nombre_empresa)
    p.setFont("Helvetica", 10)
    p.drawString(120 if config_obj and config_obj.logo else 50, height - 65, f"RUC: {ruc_empresa}")
    p.drawString(120 if config_obj and config_obj.logo else 50, height - 78, f"Telf: {telf_empresa} | {ciudad_empresa}")

    # Información de la Factura
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 50, height - 50, f"FACTURA NRO: {factura.nro_factura}")
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 50, height - 65, f"Fecha: {factura.fecha.strftime('%d/%m/%Y')}")
    p.drawRightString(width - 50, height - 78, f"Vencimiento: {factura.fecha_vencimiento.strftime('%d/%m/%Y')}")

    # Datos del Cliente
    p.line(50, height - 95, width - 50, height - 95)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 115, "CLIENTE:")
    p.setFont("Helvetica", 11)
    p.drawString(120, height - 115, str(factura.cliente.nombre if hasattr(factura.cliente, 'nombre') else factura.cliente))
    p.drawString(50, height - 130, f"ID/RUC: {factura.cliente.cedula if hasattr(factura.cliente, 'cedula') else ''}")

    # Tabla de Productos
    data = [["Producto", "Cantidad", "Precio Unit.", "Total"]]
    for item in detalles:
        data.append([
            item.producto.nombre,
            str(item.cantidad),
            f"${item.precio_unitario:,.2f}",
            f"${item.total_linea:,.2f}"
        ])

    table = Table(data, colWidths=[280, 70, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 300)

    # Totales
    y_total = height - 350
    p.drawString(width - 200, y_total, f"SUBTOTAL:")
    p.drawRightString(width - 50, y_total, f"${factura.subtotal:,.2f}")
    p.drawString(width - 200, y_total - 15, f"IVA:")
    p.drawRightString(width - 50, y_total - 15, f"${factura.iva:,.2f}")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 200, y_total - 35, f"TOTAL A PAGAR:")
    p.drawRightString(width - 50, y_total - 35, f"${factura.total:,.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

@login_required
def factura_pdf(request, pk):
    """Genera y descarga el archivo PDF de la factura."""
    factura = get_object_or_404(Factura, pk=pk)
    buffer = _generar_factura_pdf_buffer(factura)
    
    return HttpResponse(buffer, content_type='application/pdf', 
                        headers={'Content-Disposition': f'attachment; filename="factura_{factura.nro_factura}.pdf"'})

@login_required
def enviar_factura_email(request, pk):
    """Genera el PDF y lo envía automáticamente al correo electrónico del cliente."""
    factura = get_object_or_404(Factura, pk=pk)
    cliente = factura.cliente
    
    # Se intenta obtener el email del cliente (asumiendo que el campo existe en ventas.Cliente)
    email_destino = getattr(cliente, 'email', None)
    
    if not email_destino:
        messages.error(request, f"El cliente {cliente} no tiene un correo electrónico registrado.")
        return redirect('facturacion:dashboard')

    try:
        buffer = _generar_factura_pdf_buffer(factura)
        subject = f"Factura {factura.nro_factura} - {settings.ERP_CONFIG.get('EMPRESA_NOMBRE')}"
        body = f"Estimado cliente,\n\nAdjunto encontrará la factura {factura.nro_factura} correspondiente a su pedido.\n\nAtentamente,\n{settings.ERP_CONFIG.get('EMPRESA_NOMBRE')}"
        
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [email_destino])
        email.attach(f"factura_{factura.nro_factura}.pdf", buffer.getvalue(), "application/pdf")
        email.send()
        
        messages.success(request, f"Factura enviada exitosamente a {email_destino}")
    except Exception as e:
        messages.error(request, f"Error al enviar el correo: {str(e)}")
        
    return redirect('facturacion:dashboard')

@login_required
def configuracion_empresa(request):
    """Gestiona los datos básicos y el logo de la empresa."""
    instancia = ConfiguracionEmpresa.objects.first()
    if request.method == 'POST':
        form = ConfiguracionEmpresaForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada correctamente.")
            return redirect('facturacion:dashboard')
    else:
        form = ConfiguracionEmpresaForm(instance=instancia)
    
    return render(request, 'administracion/configuracion_empresa.html', {'form': form})

@login_required
def lista_usuarios(request):
    """Lista todos los usuarios del sistema."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado.")
        return redirect('core:dashboard')
    
    usuarios = User.objects.all()
    return render(request, 'administracion/usuarios/usuario_list.html', {'usuarios': usuarios})

@login_required
def editar_usuario(request, user_id=None):
    """Crea o edita un usuario."""
    if not request.user.is_superuser:
        messages.error(request, "Acceso denegado.")
        return redirect('core:dashboard')
    
    usuario = get_object_or_404(User, id=user_id) if user_id else None
    if request.method == 'POST':
        form = UserForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario guardado correctamente.")
            return redirect('administracion:lista_usuarios')
    else:
        form = UserForm(instance=usuario)
    
    return render(request, 'administracion/editar_usuario.html', {'form': form, 'usuario': usuario})
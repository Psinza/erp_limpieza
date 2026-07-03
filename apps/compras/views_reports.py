from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import cm
from .models import RetencionIVA, RetencionISLR
from apps.core.models import Empresa
import xml.etree.ElementTree as ET

def generar_pdf_retencion_iva(request, retencion_id):
    """
    Genera el comprobante de retención de IVA en PDF según Providencia 0049.
    """
    retencion = get_object_or_404(RetencionIVA, pk=retencion_id)
    empresa = Empresa.objects.first()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Retencion_IVA_{retencion.nro_comprobante}.pdf"'
    
    p = canvas.Canvas(response, pagesize=LETTER)
    width, height = LETTER

    # 1. Encabezado (Agente de Retención)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(1.5*cm, height-2*cm, empresa.nombre.upper())
    p.setFont("Helvetica", 10)
    p.drawString(1.5*cm, height-2.5*cm, f"RIF: {empresa.rif}")
    p.drawString(1.5*cm, height-3*cm, f"Dirección: {empresa.direccion[:70]}")

    # 2. Título y Nro de Comprobante
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height-4.5*cm, "COMPROBANTE DE RETENCIÓN DE I.V.A.")
    p.setFont("Helvetica", 10)
    p.drawString(14*cm, height-2*cm, f"Nro: {retencion.nro_comprobante}")
    p.drawString(14*cm, height-2.5*cm, f"Fecha: {retencion.fecha_emision.strftime('%d/%m/%Y')}")
    p.drawString(14*cm, height-3*cm, f"Periodo: {retencion.periodo_fiscal}")

    # 3. Datos del Proveedor (Sujeto Pasivo)
    p.setLineWidth(0.5)
    p.rect(1.5*cm, height-7*cm, 18.5*cm, 2*cm)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(2*cm, height-5.6*cm, f"PROVEEDOR: {retencion.proveedor.razon_social}")
    p.drawString(2*cm, height-6.2*cm, f"RIF: {retencion.proveedor.rif}")
    p.drawString(2*cm, height-6.8*cm, f"DIRECCIÓN: {retencion.proveedor.direccion[:100]}")

    # 4. Tabla de Detalles del Documento
    y = height - 8.5*cm
    p.setFont("Helvetica-Bold", 8)
    headers = ["Fecha", "Nro. Factura", "Nro. Control", "Total Compra", "Base Imponible", "IVA", "% Ret", "Monto Retenido"]
    cols = [1.5*cm, 3.5*cm, 6*cm, 8.5*cm, 11*cm, 13.5*cm, 15.5*cm, 17.5*cm]
    
    for i, head in enumerate(headers):
        p.drawString(cols[i], y, head)
    
    p.line(1.5*cm, y-0.2*cm, 20*cm, y-0.2*cm)
    
    # Fila de datos
    y -= 0.6*cm
    p.setFont("Helvetica", 8)
    p.drawString(cols[0], y, retencion.fecha_factura.strftime('%d/%m/%Y'))
    p.drawString(cols[1], y, retencion.nro_factura)
    p.drawString(cols[2], y, retencion.nro_control)
    p.drawString(cols[3], y, f"{retencion.monto_total_compra:,.2f}")
    p.drawString(cols[4], y, f"{retencion.base_imponible:,.2f}")
    p.drawString(cols[5], y, f"{retencion.monto_iva:,.2f}")
    p.drawString(cols[6], y, f"{retencion.porcentaje_retencion}%")
    p.drawString(cols[7], y, f"{retencion.monto_retenido:,.2f}")

    # 5. Firmas
    p.line(3*cm, 4*cm, 8*cm, 4*cm)
    p.drawCentredString(5.5*cm, 3.5*cm, "Agente de Retención")
    p.drawCentredString(5.5*cm, 3.1*cm, "(Firma y Sello)")

    p.line(13*cm, 4*cm, 18*cm, 4*cm)
    p.drawCentredString(15.5*cm, 3.5*cm, "Sujeto Retenido")
    p.drawCentredString(15.5*cm, 3.1*cm, "(Firma del Proveedor)")

    p.showPage()
    p.save()
    return response

def exportar_islr_xml(request, periodo):
    """
    Genera el archivo XML para la declaración mensual de ISLR.
    periodo: string en formato AAAAMM
    """
    empresa = Empresa.objects.first()
    retenciones = RetencionISLR.objects.filter(periodo_fiscal=periodo)
    
    # Limpiar RIF del Agente (solo números)
    rif_agente = empresa.rif.replace("-", "").replace(" ", "")
    
    root = ET.Element("RelacionRetencionesISLR", RifAgente=rif_agente, Periodo=periodo)
    
    for r in retenciones:
        detalle = ET.SubElement(root, "DetalleRetencion")
        ET.SubElement(detalle, "RifRetenido").text = r.proveedor.rif.replace("-", "")
        ET.SubElement(detalle, "NumeroFactura").text = r.nro_factura
        ET.SubElement(detalle, "NumeroControl").text = r.nro_control
        ET.SubElement(detalle, "FechaOperacion").text = r.fecha_factura.strftime("%d/%m/%Y")
        ET.SubElement(detalle, "CodigoConcepto").text = r.codigo_concepto
        ET.SubElement(detalle, "MontoOperacion").text = f"{r.monto_operacion:.2f}"
        ET.SubElement(detalle, "PorcentajeRetencion").text = f"{r.porcentaje_retencion:.2f}"
    
    xml_data = ET.tostring(root, encoding='utf-8', method='xml')
    
    response = HttpResponse(xml_data, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="RET_ISLR_{rif_agente}_{periodo}.xml"'
    return response
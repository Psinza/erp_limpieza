from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from django.test import RequestFactory
from apps.core.models import Usuario # Importar tu modelo de usuario personalizado
from apps.core.models import Empresa
from .views import estado_resultados_pdf, balance_general_pdf
import logging
import calendar

logger = logging.getLogger(__name__)

@shared_task
def enviar_reporte_mensual_task():
    """Tarea asíncrona para generar y enviar el reporte financiero."""
    empresa = Empresa.objects.first()
    if not empresa or not empresa.email:
        return "Error: Empresa sin email configurado."

    # Validar si es el último día del mes (importante para Celery Beat)
    hoy = timezone.now()
    _, ultimo_dia = calendar.monthrange(hoy.year, hoy.month)
    if hoy.day != ultimo_dia:
        logger.info("Tarea omitida: Hoy no es el último día del mes.")
        return f"Hoy es día {hoy.day}, el mes termina el {ultimo_dia}. Tarea saltada."

    # Simular un request para la vista de PDF
    factory = RequestFactory()
    request = factory.get('/')
    request.user = Usuario.objects.filter(is_superuser=True).first() # Usar tu modelo de usuario

    # Generar ambos reportes
    response_er = estado_resultados_pdf(request)
    response_bg = balance_general_pdf(request)

    if response_er.status_code == 200 and response_bg.status_code == 200:
        ahora = timezone.now()
        fecha_str = ahora.strftime('%m_%Y')

        email = EmailMessage(
            subject=f'Reportes Financieros Mensuales - {empresa.nombre}',
            body=f'Saludos Gerencia.\n\nSe adjuntan los reportes financieros automáticos (Estado de Resultados y Balance General) de {ahora.strftime("%B %Y")}.',
            from_email='erp_sistema@empresa.com',
            to=[empresa.email],
        )
        # Adjuntar archivos
        email.attach(f"Estado_Resultados_{fecha_str}.pdf", response_er.content, 'application/pdf')
        email.attach(f"Balance_General_{fecha_str}.pdf", response_bg.content, 'application/pdf')
        
        email.send()
        return f"Reportes enviados con éxito a {empresa.email}"

    return "Error al generar uno o ambos reportes PDF"

import os
import subprocess
import shutil
try:
    import requests
except ImportError:
    requests = None

from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from .models import RegistroRespaldo
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)

def enviar_whatsapp_alerta(mensaje):
    """
    Envía una notificación de WhatsApp ante fallos críticos.
    """
    url = getattr(settings, 'WHATSAPP_API_URL', None)
    token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
    phone = getattr(settings, 'ADMIN_PHONE_NUMBER', None)

    if not all([url, token, phone]) or requests is None:
        logger.warning("Configuración de WhatsApp incompleta o falta la librería 'requests'")
        return False

    try:
        payload = {"token": token, "to": phone, "body": mensaje}
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error enviando notificación WhatsApp: {e}")
        return False

def realizar_backup():
    """Detecta el motor de base de datos y ejecuta el respaldo correspondiente."""
    db_conf = settings.DATABASES['default']
    engine = db_conf.get('ENGINE', '')
    
    # Configuración de rutas
    respaldo_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
    if not os.path.exists(respaldo_dir):
        os.makedirs(respaldo_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if 'postgresql' in engine:
        return _backup_postgresql(db_conf, respaldo_dir, timestamp)
    elif 'sqlite3' in engine:
        return _backup_sqlite(db_conf, respaldo_dir, timestamp)
    else:
        return None, f"Motor de base de datos no soportado para respaldos: {engine}"

def _backup_postgresql(db_conf, respaldo_dir, timestamp):
    filename = f"erp_backup_pg_{timestamp}.sql"
    filepath = os.path.join(respaldo_dir, filename)
    
    env = os.environ.copy()
    env["PGPASSWORD"] = db_conf.get('PASSWORD', '')

    command = [
        'pg_dump',
        '-h', db_conf.get('HOST', 'localhost'),
        '-p', db_conf.get('PORT', '5432'),
        '-U', db_conf.get('USER', 'postgres'),
        '-f', filepath,
        '-F', 'c',  # Formato Custom (comprimido)
        db_conf.get('NAME')
    ]

    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        return filepath, None
    except Exception as e:
        error_msg = f"Error en pg_dump: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def _backup_sqlite(db_conf, respaldo_dir, timestamp):
    """Respalda una base de datos SQLite copiando el archivo .sqlite3."""
    db_path = db_conf.get('NAME')
    if not os.path.exists(db_path):
        return None, f"No se encontró el archivo de base de datos en: {db_path}"

    filename = f"erp_backup_sqlite_{timestamp}.sqlite3"
    filepath = os.path.join(respaldo_dir, filename)

    try:
        # Usamos shutil.copy2 para preservar metadatos
        shutil.copy2(db_path, filepath)
        return filepath, None
    except Exception as e:
        error_msg = f"Error copiando archivo SQLite: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def verificar_y_notificar_espacio():
    """Calcula el espacio total y envía un correo si supera los 5GB."""
    limite_mb = 5120  
    espacio_total = RegistroRespaldo.objects.filter(exitoso=True).aggregate(
        total=Sum('tamano_mb'))['total'] or 0

    if espacio_total > limite_mb:
        subject = f"ALERTA: Espacio de Respaldos Crítico ({espacio_total:.2f} MB)"
        message = f"Se ha superado el límite de 5GB de respaldos. Espacio actual: {espacio_total:.2f} MB"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL], fail_silently=True)
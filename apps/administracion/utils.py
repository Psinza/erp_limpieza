import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)

def realizar_backup_postgresql():
    """Ejecuta pg_dump para crear un respaldo comprimido de la base de datos."""
    db_conf = settings.DATABASES['default']
    
    # Configuración de rutas
    respaldo_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
    if not os.path.exists(respaldo_dir):
        os.makedirs(respaldo_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"erp_backup_{timestamp}.sql"
    filepath = os.path.join(respaldo_dir, filename)

    # Preparar entorno para pg_dump (evita pedir contraseña)
    env = os.environ.copy()
    env["PGPASSWORD"] = db_conf.get('PASSWORD', '')

    command = [
        'pg_dump',
        '-h', db_conf.get('HOST', 'localhost'),
        '-p', db_conf.get('PORT', '5432'),
        '-U', db_conf.get('USER', 'postgres'),
        '-f', filepath,
        '-F', 'c',  # Formato Custom de Postgres (comprimido)
        db_conf.get('NAME')
    ]

    try:
        process = subprocess.run(
            command, env=env, check=True, 
            capture_output=True, text=True
        )
        return filepath, None
    except subprocess.CalledProcessError as e:
        logger.error(f"Error de pg_dump: {e.stderr}")
        return None, str(e.stderr)
    except Exception as e:
        logger.error(f"Error inesperado en backup: {e}")
        return None, str(e)

def verificar_y_notificar_espacio():
    """Calcula el espacio total y envía un correo si supera los 5GB (5120 MB)."""
    from .models import RegistroRespaldo
    limite_mb = 5120  
    
    espacio_total = RegistroRespaldo.objects.filter(exitoso=True).aggregate(
        total=Sum('tamano_mb'))['total'] or 0

    if espacio_total > limite_mb:
        subject = f"ALERTA: Espacio de Respaldos Crítico ({espacio_total:.2f} MB)"
        message = (
            f"Se ha detectado que el espacio total ocupado por los respaldos de la base de datos "
            f"ha superado el límite de seguridad de 5GB.\n\n"
            f"Espacio actual: {espacio_total:.2f} MB\n"
            f"Acción recomendada: Ejecutar la limpieza de respaldos antiguos o ampliar el almacenamiento del servidor."
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )
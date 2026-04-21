import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.administracion.models import RegistroRespaldo
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Elimina automáticamente los archivos y registros de respaldo con más de 30 días de antigüedad'

    def handle(self, *args, **options):
        # Definir la fecha de corte (30 días atrás desde hoy)
        fecha_corte = timezone.now() - timedelta(days=30)
        
        # Filtrar respaldos que superen la antigüedad permitida
        respaldos_antiguos = RegistroRespaldo.objects.filter(fecha__lt=fecha_corte)
        total = respaldos_antiguos.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS('No se encontraron respaldos antiguos para eliminar.'))
            return

        for respaldo in respaldos_antiguos:
            # Eliminar el archivo físico del servidor para liberar espacio
            if respaldo.archivo and os.path.exists(respaldo.archivo.path):
                try:
                    os.remove(respaldo.archivo.path)
                except Exception as e:
                    msg = f"No se pudo borrar el archivo físico {respaldo.archivo.name}: {e}"
                    self.stdout.write(self.style.WARNING(msg))
                    logger.error(msg)
            
            # Eliminar el registro de la base de datos
            respaldo.delete()

        self.stdout.write(self.style.SUCCESS(f'Limpieza terminada: se eliminaron {total} respaldos antiguos.'))
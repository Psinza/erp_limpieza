import os
from django.core.management.base import BaseCommand
from apps.administracion.utils import realizar_backup_postgresql, verificar_y_notificar_espacio
from apps.administracion.models import RegistroRespaldo

class Command(BaseCommand):
    help = 'Genera un respaldo de la base de datos PostgreSQL'

    def handle(self, *args, **options):
        filepath, error = realizar_backup_postgresql()
        
        registro = RegistroRespaldo()
        if filepath:
            registro.nombre_original = os.path.basename(filepath)
            registro.archivo.name = f"backups/{registro.nombre_original}"
            registro.tamano_mb = os.path.getsize(filepath) / (1024 * 1024)
            registro.exitoso = True
            self.stdout.write(self.style.SUCCESS(f'Backup exitoso: {filepath}'))
        else:
            registro.exitoso = False
            registro.error_log = error
            registro.nombre_original = "FALLIDO"
            registro.tamano_mb = 0
            self.stdout.write(self.style.ERROR(f'Error en backup: {error}'))
        
        registro.save()
        if registro.exitoso:
            verificar_y_notificar_espacio()
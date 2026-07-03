from django.core.management.base import BaseCommand
from apps.contabilidad.tasks import enviar_reporte_mensual_task

class Command(BaseCommand):
    help = 'Dispara la tarea asíncrona de envío de reporte mensual.'

    def handle(self, *args, **options):
        self.stdout.write('Encolando tarea de reporte en Celery...')
        enviar_reporte_mensual_task.delay()
        self.stdout.write(self.style.SUCCESS('Tarea enviada al worker correctamente.'))
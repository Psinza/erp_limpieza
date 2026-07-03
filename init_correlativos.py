import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.facturacion.models_correlativos import CorrelativoFiscal

def init_correlativos():
    defaults = [
        ('factura', 'FAC-', 1, 6),
        ('control', 'CTRL-', 1, 6),
        ('nota_entrega', 'NE-', 1, 5),
        ('presupuesto', 'PED-', 1, 5),
    ]
    
    for tipo, prefijo, proximo, longitud in defaults:
        obj, created = CorrelativoFiscal.objects.get_or_create(
            tipo=tipo,
            defaults={
                'prefijo': prefijo,
                'proximo_numero': proximo,
                'longitud_ceros': longitud
            }
        )
        if created:
            print(f"Creado correlativo para: {tipo}")
        else:
            print(f"Correlativo ya existente para: {tipo}")

if __name__ == "__main__":
    init_correlativos()

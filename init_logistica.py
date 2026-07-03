import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.logistica.models import Almacen

def init_almacenes():
    # Almacén Materia Prima
    Almacen.objects.get_or_create(
        nombre='Almacén de Materia Prima',
        defaults={'ubicacion': 'Sector Norte, Planta 1', 'es_principal': True}
    )
    # Almacén Producto Terminado
    Almacen.objects.get_or_create(
        nombre='Almacén de Producto Terminado',
        defaults={'ubicacion': 'Sector Sur, Despacho', 'es_principal': False}
    )
    print("Almacenes inicializados correctamente.")

if __name__ == '__main__':
    init_almacenes()

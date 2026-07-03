import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.activos_fijos.models import CategoriaActivo

categorias = [
    {'nombre': 'Maquinaria y Equipos', 'prefijo_codigo': 'MAQ', 'vida_util_defecto': 10},
    {'nombre': 'Mobiliario y Equipos de Oficina', 'prefijo_codigo': 'MOB', 'vida_util_defecto': 5},
    {'nombre': 'Equipos de Computación', 'prefijo_codigo': 'COM', 'vida_util_defecto': 3},
    {'nombre': 'Vehículos', 'prefijo_codigo': 'VEH', 'vida_util_defecto': 5},
    {'nombre': 'Edificaciones', 'prefijo_codigo': 'EDI', 'vida_util_defecto': 20},
]

for cat in categorias:
    obj, created = CategoriaActivo.objects.get_or_create(nombre=cat['nombre'], defaults=cat)
    if created:
        print(f"Categoría creada: {cat['nombre']}")
    else:
        print(f"Categoría ya existe: {cat['nombre']}")

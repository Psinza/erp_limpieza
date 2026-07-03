import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.produccion.models import CategoriaMateriaPrima, CategoriaProductoTerminado

# Categorías de Materia Prima
cat_mp = [
    'Tensoactivos',
    'Ácidos / Álcalis',
    'Fragancias y Colorantes',
    'Conservantes y Quelantes',
    'Solventes',
    'Material de Empaque (Envases/Tapas)'
]

for nombre in cat_mp:
    obj, created = CategoriaMateriaPrima.objects.get_or_create(nombre=nombre)
    if created:
        print(f"Creada categoría MP: {nombre}")

# Categorías de Productos Terminados
cat_pt = [
    'Desinfectantes y Limpiadores',
    'Jabones Líquidos y Detergentes',
    'Cuidado del Automóvil',
    'Higiene y Desinfección Institucional',
    'Línea de Lavandería'
]

for nombre in cat_pt:
    obj, created = CategoriaProductoTerminado.objects.get_or_create(nombre=nombre)
    if created:
        print(f"Creada categoría PT: {nombre}")

print("Proceso de inicialización de categorías completado.")

from django.db import connection

apps_to_fix = [
    'comercializacion',
    'vendedores',
    'logistica',
    'ordenacion_pagos',
    'inventarios',
    'administracion',
]

with connection.cursor() as cursor:
    for app in apps_to_fix:
        cursor.execute("DELETE FROM django_migrations WHERE app = %s", [app])
        print(f"  Limpiado: {app}")

print("\nHistorial de migraciones limpiado para todas las apps.")

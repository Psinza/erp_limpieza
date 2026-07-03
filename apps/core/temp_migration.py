from django.http import HttpResponse
from django.core.management import call_command
import os

def run_migrations_view(request):
    # Public for a moment to fix the DB
    output = []
    try:
        # 1. Makemigrations
        call_command('makemigrations', 'activos_fijos', interactive=False)
        output.append("Makemigrations activos_fijos: SUCCESS")
        
        call_command('makemigrations', 'ventas', interactive=False)
        output.append("Makemigrations ventas: SUCCESS")
        
        # 2. Migrate
        call_command('migrate', interactive=False)
        output.append("Migrate: SUCCESS")
        
        # 3. Init logic
        try:
            from apps.activos_fijos.models import CategoriaActivo
            categorias = [
                {'nombre': 'Maquinaria y Equipos', 'prefijo_codigo': 'MAQ', 'vida_util_defecto': 10},
                {'nombre': 'Mobiliario y Equipos de Oficina', 'prefijo_codigo': 'MOB', 'vida_util_defecto': 5},
                {'nombre': 'Equipos de Computación', 'prefijo_codigo': 'COM', 'vida_util_defecto': 3},
                {'nombre': 'Vehículos', 'prefijo_codigo': 'VEH', 'vida_util_defecto': 5},
                {'nombre': 'Edificaciones', 'prefijo_codigo': 'EDI', 'vida_util_defecto': 20},
            ]
            for cat in categorias:
                CategoriaActivo.objects.get_or_create(nombre=cat['nombre'], defaults=cat)
            output.append("Init Activos: SUCCESS")
        except Exception as e_init:
            output.append(f"Init Activos WARNING: {str(e_init)}")
            
        return HttpResponse("<br>".join(output))
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

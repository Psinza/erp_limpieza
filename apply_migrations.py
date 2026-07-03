import os
import sys
import django
from django.core.management import call_command
from io import StringIO

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    out = StringIO()
    err = StringIO()
    
    print("Ejecutando makemigrations...")
    try:
        call_command('makemigrations', stdout=out, stderr=err)
    except Exception as e:
        print(f"Error en makemigrations: {e}")
        
    print("Ejecutando migrate...")
    try:
        call_command('migrate', stdout=out, stderr=err)
    except Exception as e:
        print(f"Error en migrate: {e}")
        
    with open('resultado_migraciones.txt', 'w', encoding='utf-8') as f:
        f.write("--- STDOUT ---\n")
        f.write(out.getvalue())
        f.write("\n--- STDERR ---\n")
        f.write(err.getvalue())
        
    print("Proceso finalizado. Se ha guardado el log en resultado_migraciones.txt")

if __name__ == '__main__':
    main()

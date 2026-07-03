import os
import glob
import shutil
from pathlib import Path
import django
from django.core.management import call_command

def reset_database():
    base_dir = Path(__file__).resolve().parent
    
    # 1. Eliminar db.sqlite3
    db_path = base_dir / 'db.sqlite3'
    if db_path.exists():
        print("Eliminando db.sqlite3...")
        os.remove(db_path)
    
    # 2. Eliminar todas las carpetas 'migrations' dentro de 'apps', excepto __init__.py
    apps_dir = base_dir / 'apps'
    print("Limpiando archivos de migraciones antiguos...")
    for root, dirs, files in os.walk(apps_dir):
        if 'migrations' in dirs:
            migrations_dir = Path(root) / 'migrations'
            for file in migrations_dir.iterdir():
                if file.name != '__init__.py' and file.name != '__pycache__':
                    if file.is_file():
                        file.unlink()
            # Asegurarse de que exista __init__.py
            init_file = migrations_dir / '__init__.py'
            if not init_file.exists():
                init_file.touch()

    # 3. Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # 4. Crear nuevas migraciones y aplicar
    print("Creando nuevas migraciones...")
    call_command('makemigrations')
    
    print("Aplicando migraciones a la nueva base de datos...")
    call_command('migrate')
    
    print("\n¡Base de datos reseteada con éxito!")
    print("Recuerda crear un superusuario con: python manage.py createsuperuser")

if __name__ == '__main__':
    reset_database()

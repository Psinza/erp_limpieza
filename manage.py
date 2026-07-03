#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    # Asegurar que la raíz del proyecto esté en el path de Python
    base_dir = Path(__file__).resolve().parent
    sys.path.append(str(base_dir))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
        
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y activado el entorno virtual?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
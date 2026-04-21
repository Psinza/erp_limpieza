import os
import sys
from django.core.wsgi import get_wsgi_application

# Asegurar que el directorio de aplicaciones esté en el path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
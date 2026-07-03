#!/usr/bin/env python
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.administracion.models import ConfiguracionEmpresa

# Crear configuración inicial si no existe
if not ConfiguracionEmpresa.objects.exists():
    ConfiguracionEmpresa.objects.create(
        nombre='Fábrica de Limpieza S.A.',
        nit='123456789',
        direccion='Calle Principal 123, Ciudad',
        telefono='+57 123 456 7890',
        email='info@fabricadelimpieza.com',
        moneda='$'
    )
    print("Configuración inicial de empresa creada")
else:
    print("La configuración de empresa ya existe")
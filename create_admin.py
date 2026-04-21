#!/usr/bin/env python
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Crear o actualizar usuario admin
user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
user.set_password('admin123')
user.is_superuser = True
user.is_staff = True
user.save()

print("Usuario admin creado/actualizado con contraseña admin123")
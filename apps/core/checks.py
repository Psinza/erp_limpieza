import os
import re
from django.conf import settings
from django.core.checks import Warning, register

@register()
def check_template_url_namespaces(app_configs, **kwargs):
    errors = []
    # Regex para capturar el contenido dentro de {% url '...' %} o {% url "..." %}
    url_tag_pattern = re.compile(r'{%\s*url\s+[\'"]([^\'"]+)[\'"]')
    
    # Lista de nombres de URL globales que permitimos sin namespace
    exceptions = ['login', 'logout', 'password_reset', 'admin']

    # Recorremos los directorios de plantillas definidos en el proyecto
    template_dirs = []
    for engine in settings.TEMPLATES:
        template_dirs.extend(engine.get('DIRS', []))
        if engine.get('APP_DIRS'):
            # Si APP_DIRS es True, buscamos en las carpetas templates de cada app instalada
            for app_config in app_configs or []:
                app_template_dir = os.path.join(app_config.path, 'templates')
                if os.path.isdir(app_template_dir):
                    template_dirs.append(app_template_dir)

    for directory in template_dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = url_tag_pattern.findall(content)
                        for url_name in matches:
                            # Si no contiene ':' y no está en excepciones
                            if ':' not in url_name and not any(url_name.startswith(ex) for ex in exceptions):
                                errors.append(
                                    Warning(
                                        f"La etiqueta de URL '{url_name}' no utiliza un namespace.",
                                        hint="Usa el formato 'app_name:url_name' para evitar errores de ruteo.",
                                        obj=path,
                                        id='core.W001',
                                    )
                                )
    return errors
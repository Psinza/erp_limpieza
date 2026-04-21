from django.conf import settings

def empresa_context(request):
    """Hace que los datos de la empresa estén disponibles en todos los templates."""
    # Usar configuración de settings por ahora
    class ConfigMock:
        def __init__(self):
            self.nombre = settings.ERP_CONFIG.get('EMPRESA_NOMBRE', 'ERP Industrial')
            self.logo = None
            self.ciudad = 'Ciudad'
    
    config = ConfigMock()
    return {
        'empresa_global': config,
        'nombre_erp': config.nombre
    }
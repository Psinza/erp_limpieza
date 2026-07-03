from apps.core.models import Empresa

def empresa_context(request):
    """Hace que los datos de la empresa estén disponibles en todos los templates."""
    try:
        config = Empresa.objects.first()
    except:
        config = None
    
    return {'EMPRESA': config}
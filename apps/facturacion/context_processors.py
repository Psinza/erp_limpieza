from apps.core.models import Empresa

def empresa_data(request):
    """Hace que los datos de la empresa estén disponibles en todos los templates."""
    empresa = Empresa.objects.first()
    return {
        'cfg_empresa': empresa,
    }
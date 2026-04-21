from django.core.exceptions import PermissionDenied
from functools import wraps

def permiso_requerido(modulo, accion):
    """
    Decorador para verificar permisos personalizados basados en módulos del ERP.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Lógica simple: si es superusuario tiene acceso total
            # En producción, esto debería validar contra una tabla de Permisos de Usuario
            if request.user.is_superuser or request.user.groups.filter(name=f'{modulo}_{accion}').exists():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
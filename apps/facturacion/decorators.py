from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def area_requerida(nombre_area):
    """
    Decorador para restringir el acceso a vistas basado en el área del usuario.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verifica si el usuario tiene asignada el área correspondiente
            if hasattr(request.user, 'area') and request.user.area and request.user.area.nombre == nombre_area:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, f"Acceso denegado: Se requiere pertenecer al área de {nombre_area}.")
            return redirect('core:dashboard')
        return _wrapped_view
    return decorator
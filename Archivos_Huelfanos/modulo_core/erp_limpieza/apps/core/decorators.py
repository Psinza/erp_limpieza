from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def area_requerida(*areas):
    """
    Permite acceso solo a usuarios cuya área esté en la lista,
    o a superusuarios y administradores.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('core:login')
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if user.area and user.area.codigo in areas:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tiene acceso a esta sección.')
            return redirect('core:dashboard')
        return _wrapped
    return decorator


def permiso_requerido(area_codigo, accion):
    """
    Verifica que el usuario tenga un permiso específico (área + acción).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('core:login')
            if user.tiene_permiso(area_codigo, accion):
                return view_func(request, *args, **kwargs)
            messages.error(request, f'No tiene permiso para "{accion}" en esta sección.')
            return redirect('core:dashboard')
        return _wrapped
    return decorator


def rol_requerido(*roles_nombres):
    """
    Permite acceso solo a usuarios con roles específicos.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('core:login')
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if user.rol and user.rol.nombre in roles_nombres:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Su rol no tiene acceso a esta función.')
            return redirect('core:dashboard')
        return _wrapped
    return decorator

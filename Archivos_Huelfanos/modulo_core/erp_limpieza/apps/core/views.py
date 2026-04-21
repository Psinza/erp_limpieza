from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Usuario, Rol, Area, Permiso, LogAcceso
from .forms import LoginForm, UsuarioForm, RolForm, PermisoFormSet
from .decorators import area_requerida, permiso_requerido


# ─── AUTENTICACIÓN ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        try:
            usuario_obj = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            usuario_obj = None

        if usuario_obj and usuario_obj.estado == 'BLOQUEADO':
            _log_acceso(None, username, 'BLOQUEO', request)
            messages.error(request, 'Esta cuenta está bloqueada. Contacte al administrador.')
            return render(request, 'core/login.html', {'form': form})

        user = authenticate(request, username=username, password=password)

        if user is not None and user.activo:
            login(request, user)
            user.registrar_acceso()
            _log_acceso(user, username, 'LOGIN', request)
            messages.success(request, f'Bienvenido, {user.nombre_completo}')
            return redirect(request.GET.get('next', 'core:dashboard'))
        else:
            if usuario_obj:
                usuario_obj.registrar_intento_fallido()
                _log_acceso(usuario_obj, username, 'FALLIDO', request,
                            f'Intento {usuario_obj.intentos_fallidos}/5')
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        _log_acceso(request.user, request.user.username, 'LOGOUT', request)
        logout(request)
    return redirect('core:login')


def _log_acceso(usuario, username, tipo, request, detalle=''):
    ip = _get_ip(request)
    ua = request.META.get('HTTP_USER_AGENT', '')[:500]
    LogAcceso.objects.create(
        usuario=usuario, username=username,
        tipo=tipo, ip=ip, user_agent=ua, detalle=detalle
    )


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    stats = {
        'usuarios_activos': Usuario.objects.filter(activo=True).count(),
        'roles_totales':    Rol.objects.filter(activo=True).count(),
        'areas_totales':    Area.objects.filter(activo=True).count(),
        'accesos_hoy':      LogAcceso.objects.filter(
            timestamp__date=timezone.now().date(),
            tipo='LOGIN'
        ).count(),
    }
    accesos_recientes = LogAcceso.objects.select_related('usuario')[:10]
    modulos_disponibles = _get_modulos_usuario(user)

    ctx = {
        'stats': stats,
        'accesos_recientes': accesos_recientes,
        'modulos': modulos_disponibles,
    }
    return render(request, 'core/dashboard.html', ctx)


def _get_modulos_usuario(user):
    """Retorna lista de módulos accesibles según área/rol del usuario."""
    todos = [
        {'codigo': 'RRHH',       'nombre': 'RRHH',          'icono': 'people',         'url': '#', 'color': 'primary'},
        {'codigo': 'COMPRAS',    'nombre': 'Compras',        'icono': 'cart3',          'url': '#', 'color': 'success'},
        {'codigo': 'VENTAS',     'nombre': 'Ventas',         'icono': 'graph-up-arrow', 'url': '#', 'color': 'info'},
        {'codigo': 'CONTAB',     'nombre': 'Contabilidad',   'icono': 'calculator',     'url': '#', 'color': 'warning'},
        {'codigo': 'TESORERIA',  'nombre': 'Tesorería',      'icono': 'bank',           'url': '#', 'color': 'danger'},
        {'codigo': 'PRODUCCION', 'nombre': 'Producción',     'icono': 'gear',           'url': '#', 'color': 'secondary'},
        {'codigo': 'LOGISTICA',  'nombre': 'Logística',      'icono': 'boxes',          'url': '#', 'color': 'primary'},
        {'codigo': 'TRANSPORTE', 'nombre': 'Transportes',    'icono': 'truck',          'url': '#', 'color': 'success'},
        {'codigo': 'VENDEDORES', 'nombre': 'Vendedores',     'icono': 'person-badge',   'url': '#', 'color': 'info'},
        {'codigo': 'COMERCIAL',  'nombre': 'Comercialización','icono': 'shop',          'url': '#', 'color': 'warning'},
    ]
    if user.is_superuser:
        return todos
    return [m for m in todos if user.puede_ver(m['codigo'])]


# ─── GESTIÓN DE USUARIOS ──────────────────────────────────────────────────────

@login_required
@area_requerida('ADMIN')
def usuario_lista(request):
    q = request.GET.get('q', '')
    area = request.GET.get('area', '')
    estado = request.GET.get('estado', '')

    qs = Usuario.objects.select_related('area', 'rol').all()
    if q:
        qs = qs.filter(Q(nombres__icontains=q) | Q(apellidos__icontains=q) |
                       Q(username__icontains=q) | Q(cedula__icontains=q))
    if area:
        qs = qs.filter(area__codigo=area)
    if estado:
        qs = qs.filter(estado=estado)

    ctx = {
        'usuarios': qs,
        'areas': Area.objects.filter(activo=True),
        'estados': Usuario.ESTADOS,
        'q': q, 'area_sel': area, 'estado_sel': estado,
    }
    return render(request, 'core/usuario_lista.html', ctx)


@login_required
@permiso_requerido('ADMIN', 'crear')
def usuario_crear(request):
    form = UsuarioForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        usuario = form.save(commit=False)
        usuario.set_password(form.cleaned_data['password1'])
        usuario.save()
        messages.success(request, f'Usuario {usuario.username} creado correctamente.')
        return redirect('core:usuario_lista')
    return render(request, 'core/usuario_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@permiso_requerido('ADMIN', 'editar')
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(request.POST or None, request.FILES or None,
                       instance=usuario, editar=True)
    if form.is_valid():
        form.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('core:usuario_lista')
    return render(request, 'core/usuario_form.html',
                  {'form': form, 'accion': 'Editar', 'usuario': usuario})


@login_required
@permiso_requerido('ADMIN', 'eliminar')
@require_POST
def usuario_toggle(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.activo = not usuario.activo
    usuario.estado = 'ACTIVO' if usuario.activo else 'INACTIVO'
    usuario.save(update_fields=['activo', 'estado'])
    return JsonResponse({'activo': usuario.activo, 'estado': usuario.estado})


# ─── GESTIÓN DE ROLES ─────────────────────────────────────────────────────────

@login_required
@area_requerida('ADMIN')
def rol_lista(request):
    roles = Rol.objects.prefetch_related('areas', 'permisos').annotate(
        num_usuarios=Count('usuarios')
    )
    return render(request, 'core/rol_lista.html', {'roles': roles})


@login_required
@permiso_requerido('ADMIN', 'crear')
def rol_crear(request):
    form = RolForm(request.POST or None)
    if form.is_valid():
        rol = form.save()
        messages.success(request, f'Rol "{rol.nombre}" creado correctamente.')
        return redirect('core:rol_lista')
    return render(request, 'core/rol_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@permiso_requerido('ADMIN', 'editar')
def rol_editar(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    form = RolForm(request.POST or None, instance=rol)
    if form.is_valid():
        form.save()
        messages.success(request, f'Rol "{rol.nombre}" actualizado.')
        return redirect('core:rol_lista')
    return render(request, 'core/rol_form.html',
                  {'form': form, 'accion': 'Editar', 'rol': rol})


# ─── PERFIL DEL USUARIO ACTUAL ────────────────────────────────────────────────

@login_required
def perfil(request):
    logs = LogAcceso.objects.filter(usuario=request.user).order_by('-timestamp')[:20]
    return render(request, 'core/perfil.html', {'logs': logs})


@login_required
def cambiar_password(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Contraseña cambiada exitosamente.')
        return redirect('core:perfil')
    return render(request, 'core/cambiar_password.html', {'form': form})

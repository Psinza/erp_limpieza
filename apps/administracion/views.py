from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Empresa, RegistroRespaldo
from .utils import realizar_backup, verificar_y_notificar_espacio
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    total_grupos = Group.objects.count()
    
    context = {
        'titulo': 'Administración ERP',
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_grupos': total_grupos,
    }
    return render(request, 'administracion/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def mantenimiento(request):
    """Panel de administración, soporte y backups."""
    respaldos = RegistroRespaldo.objects.all().order_by('-fecha_creacion')[:10]
    espacio_total = RegistroRespaldo.objects.filter(exitoso=True).aggregate(Sum('tamano_mb'))['tamano_mb__sum'] or 0
    porcentaje_uso = min(100, (espacio_total / 5120) * 100) # Assuming 5GB limit
    
    stats = {
        'disco_uso_porcentaje': porcentaje_uso,
        'disco_libre_gb': round((5120 - espacio_total) / 1024, 2),
        'respaldos_count': RegistroRespaldo.objects.filter(exitoso=True).count(),
        'respaldos_total_mb': round(espacio_total, 2)
    }

    log_path = os.path.join(settings.BASE_DIR, 'erp.log')
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            lines = f.readlines()
            logs = lines[-100:] if len(lines) > 100 else lines

    context = {
        'titulo': 'Mantenimiento del Sistema',
        'respaldos': respaldos,
        'espacio_total': espacio_total,
        'porcentaje_uso': porcentaje_uso,
        'stats': stats,
        'logs': logs,
    }
    return render(request, 'administracion/mantenimiento.html', context)

@login_required
@user_passes_test(is_admin)
def lista_respaldos(request):
    respaldos_list = RegistroRespaldo.objects.all().order_by('-fecha_creacion')
    paginator = Paginator(respaldos_list, 15)
    page_number = request.GET.get('page')
    respaldos = paginator.get_page(page_number)
    
    context = {
        'titulo': 'Archivos de Respaldo',
        'respaldos': respaldos
    }
    return render(request, 'administracion/lista_respaldos.html', context)

@login_required
@user_passes_test(is_admin)
def ejecutar_backup(request):
    filepath, error = realizar_backup()
    
    registro = RegistroRespaldo(creado_por=request.user)
    if filepath:
        registro.nombre_original = os.path.basename(filepath)
        registro.archivo.name = f"backups/{registro.nombre_original}"
        registro.tamano_mb = os.path.getsize(filepath) / (1024 * 1024)
        registro.exitoso = True
        messages.success(request, 'Respaldo generado exitosamente.')
    else:
        registro.exitoso = False
        registro.error_log = error
        registro.nombre_original = "FALLIDO"
        registro.tamano_mb = 0
        messages.error(request, f'Error al generar respaldo: {error}')
    
    registro.save()
    if registro.exitoso:
        verificar_y_notificar_espacio()
        
    return redirect('administracion:lista_respaldos')

@login_required
@user_passes_test(is_admin)
def download_logs(request):
    log_path = os.path.join(settings.BASE_DIR, 'erp.log')
    if os.path.exists(log_path):
        return FileResponse(open(log_path, 'rb'), as_attachment=True, filename='erp.log')
    messages.error(request, 'El archivo de log no existe.')
    return redirect('administracion:mantenimiento')

@login_required
@user_passes_test(is_admin)
def usuario_list(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'administracion/usuario_list.html', {'usuarios': usuarios})

from django.shortcuts import render, redirect, get_object_or_404

@login_required
@user_passes_test(is_admin)
def rol_list(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Group.objects.get_or_create(name=nombre)
            messages.success(request, f"Rol '{nombre}' creado exitosamente.")
        return redirect('administracion:rol_list')
    roles = Group.objects.all().order_by('name')
    return render(request, 'administracion/rol_list.html', {'roles': roles, 'titulo': 'Roles del Sistema'})

@login_required
@user_passes_test(is_admin)
def usuario_roles(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        roles_ids = request.POST.getlist('roles')
        usuario.groups.set(roles_ids)
        messages.success(request, f"Roles actualizados para {usuario.username}.")
        return redirect('administracion:usuario_list')
    roles = Group.objects.all().order_by('name')
    return render(request, 'administracion/usuario_roles.html', {'usuario': usuario, 'roles': roles, 'titulo': f'Asignar Roles: {usuario.username}'})

@login_required
@user_passes_test(is_admin)
def usuario_toggle(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario != request.user:
        usuario.is_active = not usuario.is_active
        usuario.save()
        estado = "activado" if usuario.is_active else "desactivado"
        messages.success(request, f"Usuario {usuario.username} {estado} correctamente.")
    else:
        messages.error(request, "No puedes desactivar tu propio usuario.")
    return redirect('administracion:usuario_list')

@login_required
@user_passes_test(is_admin)
def usuario_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, f'Usuario {username} creado exitosamente.')
            return redirect('administracion:usuario_list')
    return render(request, 'administracion/usuario_form.html', {'titulo': 'Nuevo Usuario'})

@login_required
@user_passes_test(is_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
    else:
        username = usuario.username
        usuario.delete()
        messages.success(request, f"Usuario {username} eliminado exitosamente.")
    return redirect('administracion:usuario_list')
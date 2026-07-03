from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ConductorForm, DespachoFinalizarForm, DespachoForm, EntregaDespachoForm,
    MantenimientoForm, PuntoEntregaForm, RutaForm, TipoVehiculoForm,
    VehiculoForm, ZonaForm,
)
from .models import (
    Conductor, Despacho, EntregaDespacho, Mantenimiento, PuntoEntrega,
    Ruta, TipoVehiculo, Vehiculo, Zona,
)


@login_required
def dashboard_transportes(request):
    stats = {
        'total_vehiculos': Vehiculo.objects.count(),
        'vehiculos_mantenimiento': Vehiculo.objects.filter(estado='mantenimiento').count(),
        'conductores_activos': Conductor.objects.filter(estado='activo').count(),
        'despachos_en_ruta': Despacho.objects.filter(estado='en_ruta').count(),
    }
    ultimos_despachos = Despacho.objects.all().order_by('-fecha_salida')[:5]
    return render(request, 'transportes/dashboard.html', {
        'titulo': 'Gestión de Flota y Logística',
        'stats': stats,
        'ultimos_despachos': ultimos_despachos
    })


def _list(request, model, template, titulo):
    return render(request, template, {'object_list': model.objects.all(), 'titulo': titulo})


def _form(request, form_class, template, titulo, instance=None, extra=None):
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        obj = form.save(commit=False)
        if hasattr(obj, 'creado_por') and not obj.creado_por_id:
            obj.creado_por = request.user
        obj.save()
        form.save_m2m()
        return redirect(request.resolver_match.namespace + ':dashboard')
    context = {'form': form, 'titulo': titulo}
    if extra:
        context.update(extra)
    return render(request, template, context)


def _detail(request, model, pk, template, titulo):
    obj = get_object_or_404(model, pk=pk)
    return render(request, template, {'object': obj, 'titulo': titulo})


def _delete(request, model, pk, template, redirect_name, titulo):
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect(redirect_name)
    return render(request, template, {'object': obj, 'titulo': titulo})


@login_required
def vehiculo_lista(request):
    return _list(request, Vehiculo, 'transportes/vehiculo_list.html', 'Vehiculos')


@login_required
def vehiculo_crear(request):
    return _form(request, VehiculoForm, 'transportes/vehiculo_form.html', 'Nuevo vehiculo')


@login_required
def vehiculo_detalle(request, pk):
    return _detail(request, Vehiculo, pk, 'transportes/vehiculo_detail.html', 'Detalle de vehiculo')


@login_required
def vehiculo_editar(request, pk):
    return _form(request, VehiculoForm, 'transportes/vehiculo_form.html', 'Editar vehiculo', get_object_or_404(Vehiculo, pk=pk))


@login_required
def vehiculo_eliminar(request, pk):
    return _delete(request, Vehiculo, pk, 'transportes/vehiculo_confirm_delete.html', 'transportes:vehiculo_list', 'Eliminar vehiculo')


@login_required
def conductor_lista(request):
    return _list(request, Conductor, 'transportes/conductor_list.html', 'Conductores')


@login_required
def conductor_crear(request):
    return _form(request, ConductorForm, 'transportes/conductor_form.html', 'Nuevo conductor')


@login_required
def conductor_detalle(request, pk):
    return _detail(request, Conductor, pk, 'transportes/conductor_detail.html', 'Detalle de conductor')


@login_required
def conductor_editar(request, pk):
    return _form(request, ConductorForm, 'transportes/conductor_form.html', 'Editar conductor', get_object_or_404(Conductor, pk=pk))


@login_required
def conductor_eliminar(request, pk):
    return _delete(request, Conductor, pk, 'transportes/conductor_confirm_delete.html', 'transportes:conductor_list', 'Eliminar conductor')


@login_required
def despacho_lista(request):
    return _list(request, Despacho, 'transportes/despacho_list.html', 'Despachos')


@login_required
def despacho_crear(request):
    return _form(request, DespachoForm, 'transportes/despacho_form.html', 'Nuevo despacho')


@login_required
def despacho_detalle(request, pk):
    return _detail(request, Despacho, pk, 'transportes/despacho_detail.html', 'Detalle de despacho')


@login_required
def despacho_editar(request, pk):
    return _form(request, DespachoForm, 'transportes/despacho_form.html', 'Editar despacho', get_object_or_404(Despacho, pk=pk))


@login_required
def despacho_finalizar(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    return _form(request, DespachoFinalizarForm, 'transportes/despacho_form.html', 'Finalizar despacho', despacho)


@login_required
def despacho_eliminar(request, pk):
    return _delete(request, Despacho, pk, 'transportes/despacho_confirm_delete.html', 'transportes:despacho_list', 'Eliminar despacho')


@login_required
def tipo_vehiculo_lista(request):
    return _list(request, TipoVehiculo, 'transportes/zona_list.html', 'Tipos de vehiculo')


@login_required
def tipo_vehiculo_crear(request):
    return _form(request, TipoVehiculoForm, 'transportes/vehiculo_form.html', 'Nuevo tipo de vehiculo')


@login_required
def tipo_vehiculo_editar(request, pk):
    return _form(request, TipoVehiculoForm, 'transportes/vehiculo_form.html', 'Editar tipo de vehiculo', get_object_or_404(TipoVehiculo, pk=pk))


@login_required
def tipo_vehiculo_eliminar(request, pk):
    return _delete(request, TipoVehiculo, pk, 'transportes/vehiculo_confirm_delete.html', 'transportes:tipo_vehiculo_list', 'Eliminar tipo')


@login_required
def zona_lista(request):
    return _list(request, Zona, 'transportes/zona_list.html', 'Zonas')


@login_required
def zona_crear(request):
    return _form(request, ZonaForm, 'transportes/ruta_form.html', 'Nueva zona')


@login_required
def zona_editar(request, pk):
    return _form(request, ZonaForm, 'transportes/ruta_form.html', 'Editar zona', get_object_or_404(Zona, pk=pk))


@login_required
def zona_eliminar(request, pk):
    return _delete(request, Zona, pk, 'transportes/vehiculo_confirm_delete.html', 'transportes:zona_list', 'Eliminar zona')


@login_required
def ruta_lista(request):
    return _list(request, Ruta, 'transportes/ruta_list.html', 'Rutas')


@login_required
def ruta_crear(request):
    return _form(request, RutaForm, 'transportes/ruta_form.html', 'Nueva ruta')


@login_required
def ruta_detalle(request, pk):
    return _detail(request, Ruta, pk, 'transportes/ruta_detail.html', 'Detalle de ruta')


@login_required
def ruta_editar(request, pk):
    return _form(request, RutaForm, 'transportes/ruta_form.html', 'Editar ruta', get_object_or_404(Ruta, pk=pk))


@login_required
def ruta_eliminar(request, pk):
    return _delete(request, Ruta, pk, 'transportes/vehiculo_confirm_delete.html', 'transportes:ruta_list', 'Eliminar ruta')


@login_required
def punto_entrega_crear(request, ruta_pk):
    ruta = get_object_or_404(Ruta, pk=ruta_pk)
    return _form(request, PuntoEntregaForm, 'transportes/ruta_form.html', 'Nuevo punto de entrega', extra={'ruta': ruta})


@login_required
def punto_entrega_editar(request, pk):
    return _form(request, PuntoEntregaForm, 'transportes/ruta_form.html', 'Editar punto de entrega', get_object_or_404(PuntoEntrega, pk=pk))


@login_required
def punto_entrega_eliminar(request, pk):
    return _delete(request, PuntoEntrega, pk, 'transportes/vehiculo_confirm_delete.html', 'transportes:ruta_list', 'Eliminar punto')


@login_required
def mantenimiento_lista(request):
    return _list(request, Mantenimiento, 'transportes/mantenimiento_list.html', 'Mantenimientos')


@login_required
def mantenimiento_crear(request):
    return _form(request, MantenimientoForm, 'transportes/mantenimiento_form.html', 'Nuevo mantenimiento')


@login_required
def mantenimiento_detalle(request, pk):
    return _detail(request, Mantenimiento, pk, 'transportes/mantenimiento_list.html', 'Detalle de mantenimiento')


@login_required
def mantenimiento_editar(request, pk):
    return _form(request, MantenimientoForm, 'transportes/mantenimiento_form.html', 'Editar mantenimiento', get_object_or_404(Mantenimiento, pk=pk))


@login_required
def mantenimiento_eliminar(request, pk):
    return _delete(request, Mantenimiento, pk, 'transportes/vehiculo_confirm_delete.html', 'transportes:mantenimiento_list', 'Eliminar mantenimiento')


@login_required
def entrega_despacho_crear(request, despacho_pk):
    despacho = get_object_or_404(Despacho, pk=despacho_pk)
    return _form(request, EntregaDespachoForm, 'transportes/despacho_form.html', 'Nueva entrega', extra={'despacho': despacho})


@login_required
def entrega_despacho_editar(request, pk):
    return _form(request, EntregaDespachoForm, 'transportes/despacho_form.html', 'Editar entrega', get_object_or_404(EntregaDespacho, pk=pk))


@login_required
def entrega_despacho_eliminar(request, pk):
    return _delete(request, EntregaDespacho, pk, 'transportes/despacho_confirm_delete.html', 'transportes:despacho_list', 'Eliminar entrega')

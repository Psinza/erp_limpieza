# apps/rrhh/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Empleado, Departamento, Nomina, NominaDetalle, Vacacion
from .forms import EmpleadoForm, DepartamentoForm, NominaForm, VacacionForm
from apps.core.decorators import permiso_requerido

@login_required
@permiso_requerido('RRHH', 'ver')
def dashboard_rrhh(request):
    total_empleados = Empleado.objects.filter(activo=True).count()
    empleados_recientes = Empleado.objects.all().order_by('-id')[:5]
    total_nominas = Nomina.objects.count()
    total_vacaciones_pend = Vacacion.objects.filter(estado='pendiente').count()
    
    return render(request, "rrhh/dashboard_rrhh.html", {
        "total_empleados": total_empleados,
        "empleados_recientes": empleados_recientes,
        "total_nominas": total_nominas,
        "total_vacaciones_pend": total_vacaciones_pend,
    })

@login_required
def departamento_list(request):
    qs = Departamento.objects.all()
    return render(request, "rrhh/departamento_list.html", {"departamentos": qs})

@login_required
def departamento_create(request):
    form = DepartamentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Departamento creado correctamente.")
        return redirect("rrhh:departamento_list")
    return render(request, "rrhh/departamento_form.html", {"form": form, "titulo": "Nuevo Departamento"})

@login_required
def empleado_list(request):
    qs = Empleado.objects.all()
    return render(request, "rrhh/empleado_list.html", {"empleados": qs})

@login_required
def empleado_create(request):
    form = EmpleadoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Empleado creado.")
        return redirect("rrhh:empleado_list")
    return render(request, "rrhh/empleado_form.html", {"form": form, "titulo": "Nuevo Empleado"})

@login_required
def nomina_list(request):
    nominas = Nomina.objects.all().order_by('-anio', '-mes')
    return render(request, "rrhh/nomina_list.html", {"nominas": nominas})

@login_required
def nomina_create(request):
    form = NominaForm(request.POST or None)
    if form.is_valid():
        nomina = form.save()
        # Generación automática de detalles para empleados activos
        empleados = Empleado.objects.filter(activo=True)
        total = 0
        for emp in empleados:
            NominaDetalle.objects.create(
                nomina=nomina,
                empleado=emp,
                sueldo_base=emp.sueldo,
                neto_recibir=emp.sueldo
            )
            total += emp.sueldo
        nomina.total_nomina = total
        nomina.save()
        messages.success(request, f"Nómina de {nomina.get_mes_display()} {nomina.anio} generada con éxito.")
        return redirect("rrhh:nomina_list")
    return render(request, "rrhh/nomina_form.html", {"form": form, "titulo": "Nueva Nómina"})

@login_required
def vacacion_list(request):
    vacaciones = Vacacion.objects.all().order_by('-fecha_inicio')
    return render(request, "rrhh/vacacion_list.html", {"vacaciones": vacaciones})

@login_required
def vacacion_create(request):
    form = VacacionForm(request.POST or None)
    if form.is_valid():
        vacacion = form.save(commit=False)
        delta = vacacion.fecha_fin - vacacion.fecha_inicio
        vacacion.dias_solicitados = delta.days + 1
        vacacion.save()
        messages.success(request, "Solicitud de vacaciones registrada.")
        return redirect("rrhh:vacacion_list")
    return render(request, "rrhh/vacacion_form.html", {"form": form, "titulo": "Nueva Solicitud de Vacaciones"})

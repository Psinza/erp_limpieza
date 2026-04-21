# apps/contabilidad/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

from .models import (
    EjercicioContable, CuentaContable,
    AsientoContable, LineaAsiento,
    PeriodoContable, ConfiguracionContable,
)
from .forms import (
    EjercicioContableForm, CuentaContableForm,
    AsientoContableForm, LineaAsientoForm,
    PeriodoContableForm, ConfiguracionContableForm,
    FiltroReporteForm,
)


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
@login_required
def dashboard_contabilidad(request):
    ejercicio_activo = EjercicioContable.objects.filter(estado="abierto").first()
    total_asientos   = AsientoContable.objects.filter(estado="aprobado").count()
    asientos_pend    = AsientoContable.objects.filter(estado="borrador").count()
    total_cuentas    = CuentaContable.objects.filter(activa=True).count()

    ultimos_asientos = AsientoContable.objects.select_related(
        "ejercicio", "creado_por"
    ).order_by("-fecha", "-numero")[:8]

    # Totales por tipo de cuenta
    saldos_tipo = {}
    for tipo, label in CuentaContable.TIPO_CHOICES:
        saldo = CuentaContable.objects.filter(
            tipo=tipo, activa=True, acepta_movimientos=True
        ).aggregate(total=Sum("saldo_actual"))["total"] or Decimal("0.00")
        saldos_tipo[tipo] = {"label": label, "saldo": saldo}

    return render(request, "contabilidad/dashboard_contabilidad.html", {
        "ejercicio_activo": ejercicio_activo,
        "total_asientos":   total_asientos,
        "asientos_pend":    asientos_pend,
        "total_cuentas":    total_cuentas,
        "ultimos_asientos": ultimos_asientos,
        "saldos_tipo":      saldos_tipo,
    })


# ─────────────────────────────────────────────
#  EJERCICIOS CONTABLES
# ─────────────────────────────────────────────
@login_required
def ejercicio_list(request):
    ejercicios = EjercicioContable.objects.all()
    return render(request, "contabilidad/ejercicio_list.html", {"ejercicios": ejercicios})


@login_required
def ejercicio_create(request):
    form = EjercicioContableForm(request.POST or None)
    if form.is_valid():
        ej = form.save(commit=False)
        ej.creado_por = request.user
        ej.save()
        messages.success(request, f"Ejercicio '{ej.nombre}' creado.")
        return redirect("contabilidad:ejercicio_list")
    return render(request, "contabilidad/ejercicio_form.html",
                  {"form": form, "titulo": "Nuevo Ejercicio Contable"})


@login_required
def ejercicio_cerrar(request, pk):
    ej = get_object_or_404(EjercicioContable, pk=pk)
    if request.method == "POST":
        if ej.estado == "abierto":
            ej.estado = "cerrado"
            ej.save()
            messages.warning(request, f"Ejercicio '{ej.nombre}' cerrado.")
        else:
            messages.error(request, "El ejercicio ya está cerrado.")
    return redirect("contabilidad:ejercicio_list")


# ─────────────────────────────────────────────
#  PLAN DE CUENTAS
# ─────────────────────────────────────────────
@login_required
def plan_cuentas(request):
    q    = request.GET.get("q", "")
    tipo = request.GET.get("tipo", "")

    qs = CuentaContable.objects.filter(activa=True)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    if tipo:
        qs = qs.filter(tipo=tipo)

    return render(request, "contabilidad/plan_cuentas.html", {
        "cuentas": qs, "q": q, "tipo": tipo,
        "tipos": CuentaContable.TIPO_CHOICES,
    })


@login_required
def cuenta_create(request):
    form = CuentaContableForm(request.POST or None)
    if form.is_valid():
        cuenta = form.save(commit=False)
        cuenta.saldo_actual = cuenta.saldo_inicial
        cuenta.save()
        messages.success(request, f"Cuenta '{cuenta.codigo} — {cuenta.nombre}' creada.")
        return redirect("contabilidad:plan_cuentas")
    return render(request, "contabilidad/cuenta_form.html",
                  {"form": form, "titulo": "Nueva Cuenta Contable"})


@login_required
def cuenta_edit(request, pk):
    cuenta = get_object_or_404(CuentaContable, pk=pk)
    form   = CuentaContableForm(request.POST or None, instance=cuenta)
    if form.is_valid():
        form.save()
        messages.success(request, "Cuenta actualizada.")
        return redirect("contabilidad:plan_cuentas")
    return render(request, "contabilidad/cuenta_form.html",
                  {"form": form, "titulo": "Editar Cuenta", "cuenta": cuenta})


@login_required
def cuenta_mayor(request, pk):
    """Libro mayor de una cuenta: todos los movimientos."""
    cuenta   = get_object_or_404(CuentaContable, pk=pk)
    ejercicio_id = request.GET.get("ejercicio", "")
    lineas   = LineaAsiento.objects.filter(
        cuenta=cuenta,
        asiento__estado="aprobado"
    ).select_related("asiento").order_by("asiento__fecha", "asiento__numero")

    if ejercicio_id:
        lineas = lineas.filter(asiento__ejercicio__id=ejercicio_id)

    ejercicios = EjercicioContable.objects.all()
    debe_total  = lineas.filter(tipo="debe").aggregate(t=Sum("monto"))["t"] or Decimal("0.00")
    haber_total = lineas.filter(tipo="haber").aggregate(t=Sum("monto"))["t"] or Decimal("0.00")

    return render(request, "contabilidad/cuenta_mayor.html", {
        "cuenta": cuenta, "lineas": lineas,
        "debe_total": debe_total, "haber_total": haber_total,
        "ejercicios": ejercicios, "ejercicio_id": ejercicio_id,
    })


# ─────────────────────────────────────────────
#  ASIENTOS CONTABLES
# ─────────────────────────────────────────────
@login_required
def asiento_list(request):
    q       = request.GET.get("q", "")
    estado  = request.GET.get("estado", "")
    ejerc   = request.GET.get("ejercicio", "")

    qs = AsientoContable.objects.select_related("ejercicio", "creado_por")
    if q:
        qs = qs.filter(
            Q(numero__icontains=q)  |
            Q(concepto__icontains=q)|
            Q(referencia__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    if ejerc:
        qs = qs.filter(ejercicio__id=ejerc)

    ejercicios = EjercicioContable.objects.all()
    return render(request, "contabilidad/asiento_list.html", {
        "asientos": qs, "q": q, "estado": estado, "ejerc": ejerc,
        "estados":    AsientoContable.ESTADO_CHOICES,
        "ejercicios": ejercicios,
    })


@login_required
def asiento_create(request):
    form = AsientoContableForm(request.POST or None)
    if form.is_valid():
        ast = form.save(commit=False)
        ast.numero     = AsientoContable.generar_numero()
        ast.creado_por = request.user
        ast.save()
        messages.success(request, f"Asiento AST-{ast.numero} creado.")
        return redirect("contabilidad:asiento_detail", pk=ast.pk)
    return render(request, "contabilidad/asiento_form.html",
                  {"form": form, "titulo": "Nuevo Asiento Contable"})


@login_required
def asiento_detail(request, pk):
    asiento  = get_object_or_404(AsientoContable, pk=pk)
    lineas   = asiento.lineas.select_related("cuenta").order_by("tipo", "cuenta__codigo")
    lin_form = LineaAsientoForm()
    return render(request, "contabilidad/asiento_detail.html", {
        "asiento": asiento, "lineas": lineas, "lin_form": lin_form,
    })


@login_required
def asiento_agregar_linea(request, pk):
    asiento = get_object_or_404(AsientoContable, pk=pk)
    if asiento.estado != "borrador":
        messages.error(request, "Solo se pueden agregar líneas en asientos Borrador.")
        return redirect("contabilidad:asiento_detail", pk=pk)
    form = LineaAsientoForm(request.POST)
    if form.is_valid():
        linea         = form.save(commit=False)
        linea.asiento = asiento
        linea.save()
        asiento.calcular_totales()
        messages.success(request,
            f"Línea agregada: {linea.cuenta} {linea.get_tipo_display()} ${linea.monto}")
    else:
        messages.error(request, f"Error: {form.errors}")
    return redirect("contabilidad:asiento_detail", pk=pk)


@login_required
def asiento_eliminar_linea(request, pk, lpk):
    asiento = get_object_or_404(AsientoContable, pk=pk)
    linea   = get_object_or_404(LineaAsiento, pk=lpk, asiento=asiento)
    if request.method == "POST":
        if asiento.estado == "borrador":
            linea.delete()
            asiento.calcular_totales()
            messages.warning(request, "Línea eliminada.")
        else:
            messages.error(request, "No se puede eliminar líneas de un asiento aprobado.")
    return redirect("contabilidad:asiento_detail", pk=pk)


@login_required
def asiento_aprobar(request, pk):
    asiento = get_object_or_404(AsientoContable, pk=pk)
    if asiento.estado != "borrador":
        messages.error(request, "El asiento no está en Borrador.")
        return redirect("contabilidad:asiento_detail", pk=pk)
    if not asiento.lineas.exists():
        messages.error(request, "El asiento no tiene líneas.")
        return redirect("contabilidad:asiento_detail", pk=pk)
    try:
        asiento.aprobar(request.user)
        messages.success(request,
            f"Asiento AST-{asiento.numero} aprobado. Saldos actualizados.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("contabilidad:asiento_detail", pk=pk)


@login_required
def asiento_anular(request, pk):
    asiento = get_object_or_404(AsientoContable, pk=pk)
    if request.method == "POST":
        if asiento.estado != "anulado":
            asiento.anular()
            messages.warning(request, f"Asiento AST-{asiento.numero} anulado.")
        else:
            messages.error(request, "El asiento ya está anulado.")
    return redirect("contabilidad:asiento_detail", pk=pk)


# ─────────────────────────────────────────────
#  LIBRO DIARIO
# ─────────────────────────────────────────────
@login_required
def libro_diario(request):
    form      = FiltroReporteForm(request.GET or None)
    asientos  = AsientoContable.objects.none()
    ejercicio = None

    if form.is_valid():
        ejercicio = form.cleaned_data["ejercicio"]
        qs        = AsientoContable.objects.filter(
            ejercicio=ejercicio, estado="aprobado"
        ).prefetch_related("lineas__cuenta").order_by("fecha", "numero")

        fi = form.cleaned_data.get("fecha_inicio")
        ff = form.cleaned_data.get("fecha_fin")
        if fi:
            qs = qs.filter(fecha__gte=fi)
        if ff:
            qs = qs.filter(fecha__lte=ff)
        asientos = qs

    return render(request, "contabilidad/libro_diario.html", {
        "form": form, "asientos": asientos, "ejercicio": ejercicio,
    })


# ─────────────────────────────────────────────
#  BALANCE DE COMPROBACIÓN
# ─────────────────────────────────────────────
@login_required
def balance_comprobacion(request):
    form      = FiltroReporteForm(request.GET or None)
    cuentas   = []
    ejercicio = None
    totales   = {"debe": Decimal("0.00"), "haber": Decimal("0.00"), "saldo_d": Decimal("0.00"), "saldo_h": Decimal("0.00")}

    if form.is_valid():
        ejercicio = form.cleaned_data["ejercicio"]
        fi = form.cleaned_data.get("fecha_inicio")
        ff = form.cleaned_data.get("fecha_fin")

        lineas_qs = LineaAsiento.objects.filter(
            asiento__ejercicio=ejercicio,
            asiento__estado="aprobado"
        )
        if fi:
            lineas_qs = lineas_qs.filter(asiento__fecha__gte=fi)
        if ff:
            lineas_qs = lineas_qs.filter(asiento__fecha__lte=ff)

        # Agrupar por cuenta
        from django.db.models import Sum, Case, When, DecimalField as DF
        resumen = (
            lineas_qs
            .values("cuenta__codigo", "cuenta__nombre", "cuenta__tipo",
                    "cuenta__naturaleza")
            .annotate(
                debe=Sum(Case(When(tipo="debe", then="monto"), output_field=DF())),
                haber=Sum(Case(When(tipo="haber", then="monto"), output_field=DF())),
            )
            .order_by("cuenta__codigo")
        )

        for row in resumen:
            debe  = row["debe"]  or Decimal("0.00")
            haber = row["haber"] or Decimal("0.00")
            if row["cuenta__naturaleza"] == "deudora":
                saldo = debe - haber
                sd = max(saldo, Decimal("0.00"))
                sh = Decimal("0.00") if saldo >= 0 else abs(saldo)
            else:
                saldo = haber - debe
                sh = max(saldo, Decimal("0.00"))
                sd = Decimal("0.00") if saldo >= 0 else abs(saldo)

            cuentas.append({
                "codigo":    row["cuenta__codigo"],
                "nombre":    row["cuenta__nombre"],
                "tipo":      row["cuenta__tipo"],
                "debe":      debe,
                "haber":     haber,
                "saldo_d":   sd,
                "saldo_h":   sh,
            })
            totales["debe"]    += debe
            totales["haber"]   += haber
            totales["saldo_d"] += sd
            totales["saldo_h"] += sh

    return render(request, "contabilidad/balance_comprobacion.html", {
        "form": form, "cuentas": cuentas, "totales": totales, "ejercicio": ejercicio,
    })


# ─────────────────────────────────────────────
#  ESTADO DE RESULTADOS
# ─────────────────────────────────────────────
@login_required
def estado_resultados(request):
    form        = FiltroReporteForm(request.GET or None)
    ejercicio   = None
    ingresos    = []
    costos      = []
    gastos      = []
    total_ing   = Decimal("0.00")
    total_costo = Decimal("0.00")
    total_gasto = Decimal("0.00")
    utilidad    = Decimal("0.00")

    if form.is_valid():
        ejercicio = form.cleaned_data["ejercicio"]
        fi = form.cleaned_data.get("fecha_inicio")
        ff = form.cleaned_data.get("fecha_fin")

        from django.db.models import Sum, Case, When, DecimalField as DF

        def _saldo_cuentas(tipos):
            qs = LineaAsiento.objects.filter(
                asiento__ejercicio=ejercicio,
                asiento__estado="aprobado",
                cuenta__tipo__in=tipos,
            )
            if fi:
                qs = qs.filter(asiento__fecha__gte=fi)
            if ff:
                qs = qs.filter(asiento__fecha__lte=ff)
            return (
                qs.values("cuenta__codigo", "cuenta__nombre", "cuenta__tipo",
                          "cuenta__naturaleza")
                .annotate(
                    debe=Sum(Case(When(tipo="debe", then="monto"), output_field=DF())),
                    haber=Sum(Case(When(tipo="haber", then="monto"), output_field=DF())),
                )
                .order_by("cuenta__codigo")
            )

        def _neto(row):
            debe  = row["debe"]  or Decimal("0.00")
            haber = row["haber"] or Decimal("0.00")
            if row["cuenta__naturaleza"] == "acreedora":
                return haber - debe
            return debe - haber

        for row in _saldo_cuentas(["ingreso"]):
            neto = _neto(row)
            ingresos.append({**row, "neto": neto})
            total_ing += neto

        for row in _saldo_cuentas(["costo"]):
            neto = _neto(row)
            costos.append({**row, "neto": neto})
            total_costo += neto

        for row in _saldo_cuentas(["egreso"]):
            neto = _neto(row)
            gastos.append({**row, "neto": neto})
            total_gasto += neto

        utilidad_bruta = total_ing - total_costo
        utilidad       = utilidad_bruta - total_gasto

    return render(request, "contabilidad/estado_resultados.html", {
        "form": form, "ejercicio": ejercicio,
        "ingresos":  ingresos,  "total_ing":   total_ing,
        "costos":    costos,    "total_costo": total_costo,
        "gastos":    gastos,    "total_gasto": total_gasto,
        "utilidad_bruta": total_ing - total_costo,
        "utilidad":       utilidad,
    })


# ─────────────────────────────────────────────
#  BALANCE GENERAL
# ─────────────────────────────────────────────
@login_required
def balance_general(request):
    form       = FiltroReporteForm(request.GET or None)
    ejercicio  = None
    activos    = []
    pasivos    = []
    patrimonio = []
    total_activo    = Decimal("0.00")
    total_pasivo    = Decimal("0.00")
    total_patrimonio= Decimal("0.00")

    if form.is_valid():
        ejercicio = form.cleaned_data["ejercicio"]
        fi = form.cleaned_data.get("fecha_inicio")
        ff = form.cleaned_data.get("fecha_fin")

        from django.db.models import Sum, Case, When, DecimalField as DF

        def _cuentas_con_saldo(tipos):
            qs = LineaAsiento.objects.filter(
                asiento__ejercicio=ejercicio,
                asiento__estado="aprobado",
                cuenta__tipo__in=tipos,
            )
            if fi:
                qs = qs.filter(asiento__fecha__gte=fi)
            if ff:
                qs = qs.filter(asiento__fecha__lte=ff)
            rows = (
                qs.values("cuenta__codigo", "cuenta__nombre",
                          "cuenta__tipo", "cuenta__naturaleza",
                          "cuenta__saldo_inicial")
                .annotate(
                    debe=Sum(Case(When(tipo="debe", then="monto"), output_field=DF())),
                    haber=Sum(Case(When(tipo="haber", then="monto"), output_field=DF())),
                )
                .order_by("cuenta__codigo")
            )
            result = []
            for row in rows:
                debe  = row["debe"]  or Decimal("0.00")
                haber = row["haber"] or Decimal("0.00")
                si    = row["cuenta__saldo_inicial"] or Decimal("0.00")
                if row["cuenta__naturaleza"] == "deudora":
                    saldo = si + debe - haber
                else:
                    saldo = si + haber - debe
                result.append({**row, "saldo": saldo})
            return result

        activos     = _cuentas_con_saldo(["activo"])
        pasivos     = _cuentas_con_saldo(["pasivo"])
        patrimonio  = _cuentas_con_saldo(["patrimonio"])

        total_activo     = sum(r["saldo"] for r in activos)
        total_pasivo     = sum(r["saldo"] for r in pasivos)
        total_patrimonio = sum(r["saldo"] for r in patrimonio)

    return render(request, "contabilidad/balance_general.html", {
        "form": form, "ejercicio": ejercicio,
        "activos":    activos,    "total_activo":     total_activo,
        "pasivos":    pasivos,    "total_pasivo":     total_pasivo,
        "patrimonio": patrimonio, "total_patrimonio": total_patrimonio,
        "total_pasivo_patrimonio": total_pasivo + total_patrimonio,
    })


# ─────────────────────────────────────────────
#  CONFIGURACIÓN CONTABLE
# ─────────────────────────────────────────────
@login_required
def configuracion_list(request):
    configs = ConfiguracionContable.objects.select_related("cuenta").all()
    return render(request, "contabilidad/configuracion_list.html", {"configs": configs})


@login_required
def configuracion_create(request):
    form = ConfiguracionContableForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Configuración creada.")
        return redirect("contabilidad:configuracion_list")
    return render(request, "contabilidad/configuracion_form.html",
                  {"form": form, "titulo": "Nueva Configuración"})


@login_required
def configuracion_edit(request, pk):
    cfg  = get_object_or_404(ConfiguracionContable, pk=pk)
    form = ConfiguracionContableForm(request.POST or None, instance=cfg)
    if form.is_valid():
        form.save()
        messages.success(request, "Configuración actualizada.")
        return redirect("contabilidad:configuracion_list")
    return render(request, "contabilidad/configuracion_form.html",
                  {"form": form, "titulo": "Editar Configuración"})

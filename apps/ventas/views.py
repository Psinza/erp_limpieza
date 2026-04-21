# apps/ventas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal

from .models import (
    CategoriaCliente, Cliente, ContactoCliente,
    CategoriaProductoVenta, ProductoVenta,
    Cotizacion, DetalleCotizacion,
    Pedido, DetallePedido,
    Despacho, DetalleDespacho,
)
from .forms import (
    CategoriaClienteForm, ClienteForm, ContactoClienteForm,
    CategoriaProductoVentaForm, ProductoVentaForm,
    CotizacionForm, DetalleCotizacionForm,
    PedidoForm, DetallePedidoForm,
    DespachoForm, DetalleDespachoForm,
)


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
@login_required
def dashboard_ventas(request):
    hoy            = timezone.now()
    total_clientes = Cliente.objects.filter(estado="activo").count()
    pedidos_activos= Pedido.objects.exclude(estado__in=["entregado","facturado","anulado"]).count()
    ventas_mes     = (
        Pedido.objects
        .filter(fecha_pedido__month=hoy.month, fecha_pedido__year=hoy.year)
        .exclude(estado="anulado")
        .aggregate(Sum("total"))["total__sum"] or Decimal("0.00")
    )
    cotizaciones_pend = Cotizacion.objects.filter(estado__in=["borrador","enviada"]).count()

    ultimos_pedidos   = Pedido.objects.select_related("cliente").order_by("-creado_en")[:6]
    ultimas_cotizaciones = Cotizacion.objects.select_related("cliente").order_by("-creado_en")[:5]
    top_clientes      = (
        Cliente.objects.filter(estado="activo")
        .annotate(num_pedidos=Count("pedidos"))
        .order_by("-num_pedidos")[:5]
    )

    return render(request, "ventas/dashboard_ventas.html", {
        "total_clientes":      total_clientes,
        "pedidos_activos":     pedidos_activos,
        "ventas_mes":          ventas_mes,
        "cotizaciones_pend":   cotizaciones_pend,
        "ultimos_pedidos":     ultimos_pedidos,
        "ultimas_cotizaciones":ultimas_cotizaciones,
        "top_clientes":        top_clientes,
    })


# ─────────────────────────────────────────────
#  CATEGORÍAS CLIENTE
# ─────────────────────────────────────────────
@login_required
def categoria_cliente_list(request):
    cats = CategoriaCliente.objects.annotate(num=Count("clientes"))
    return render(request, "ventas/categoria_cliente_list.html", {"categorias": cats})


@login_required
def categoria_cliente_create(request):
    form = CategoriaClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoría creada.")
        return redirect("ventas:categoria_cliente_list")
    return render(request, "ventas/categoria_cliente_form.html",
                  {"form": form, "titulo": "Nueva Categoría de Cliente"})


@login_required
def categoria_cliente_edit(request, pk):
    obj  = get_object_or_404(CategoriaCliente, pk=pk)
    form = CategoriaClienteForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoría actualizada.")
        return redirect("ventas:categoria_cliente_list")
    return render(request, "ventas/categoria_cliente_form.html",
                  {"form": form, "titulo": "Editar Categoría"})


# ─────────────────────────────────────────────
#  CLIENTES
# ─────────────────────────────────────────────
@login_required
def cliente_list(request):
    q      = request.GET.get("q", "")
    estado = request.GET.get("estado", "")
    cat    = request.GET.get("categoria", "")

    qs = Cliente.objects.select_related("categoria", "vendedor")
    if q:
        qs = qs.filter(
            Q(razon_social__icontains=q) |
            Q(ruc__icontains=q)          |
            Q(nombre_comercial__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    if cat:
        qs = qs.filter(categoria__id=cat)

    categorias = CategoriaCliente.objects.all()
    return render(request, "ventas/cliente_list.html", {
        "clientes": qs, "categorias": categorias,
        "q": q, "estado": estado, "cat": cat,
    })


@login_required
def cliente_detail(request, pk):
    cli       = get_object_or_404(Cliente, pk=pk)
    contactos = cli.contactos.all()
    pedidos   = cli.pedidos.order_by("-fecha_pedido")[:10]
    cotizaciones = cli.cotizaciones.order_by("-fecha_emision")[:5]
    totales   = cli.pedidos.exclude(estado="anulado").aggregate(
        total_comprado=Sum("total"), num_pedidos=Count("id")
    )
    return render(request, "ventas/cliente_detail.html", {
        "cli": cli, "contactos": contactos,
        "pedidos": pedidos, "cotizaciones": cotizaciones,
        "totales": totales,
    })


@login_required
def cliente_create(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        cli = form.save(commit=False)
        cli.creado_por = request.user
        cli.save()
        messages.success(request, f"Cliente '{cli.razon_social}' creado.")
        return redirect("ventas:cliente_detail", pk=cli.pk)
    return render(request, "ventas/cliente_form.html",
                  {"form": form, "titulo": "Nuevo Cliente"})


@login_required
def cliente_edit(request, pk):
    cli  = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cli)
    if form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado.")
        return redirect("ventas:cliente_detail", pk=cli.pk)
    return render(request, "ventas/cliente_form.html",
                  {"form": form, "titulo": "Editar Cliente", "cli": cli})


@login_required
def cliente_contacto_add(request, pk):
    cli  = get_object_or_404(Cliente, pk=pk)
    form = ContactoClienteForm(request.POST or None)
    if form.is_valid():
        c = form.save(commit=False)
        c.cliente = cli
        c.save()
        messages.success(request, "Contacto agregado.")
        return redirect("ventas:cliente_detail", pk=pk)
    return render(request, "ventas/contacto_cliente_form.html",
                  {"form": form, "cli": cli})


@login_required
def cliente_contacto_delete(request, pk, cpk):
    contacto = get_object_or_404(ContactoCliente, pk=cpk, cliente__pk=pk)
    if request.method == "POST":
        contacto.delete()
        messages.warning(request, "Contacto eliminado.")
    return redirect("ventas:cliente_detail", pk=pk)


# ─────────────────────────────────────────────
#  PRODUCTOS DE VENTA
# ─────────────────────────────────────────────
@login_required
def producto_list(request):
    q   = request.GET.get("q", "")
    cat = request.GET.get("categoria", "")
    qs  = ProductoVenta.objects.select_related("categoria")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    if cat:
        qs = qs.filter(categoria__id=cat)
    categorias = CategoriaProductoVenta.objects.all()
    return render(request, "ventas/producto_list.html", {
        "productos": qs, "categorias": categorias, "q": q, "cat": cat,
    })


@login_required
def producto_create(request):
    form = ProductoVentaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Producto creado.")
        return redirect("ventas:producto_list")
    return render(request, "ventas/producto_form.html",
                  {"form": form, "titulo": "Nuevo Producto de Venta"})


@login_required
def producto_edit(request, pk):
    obj  = get_object_or_404(ProductoVenta, pk=pk)
    form = ProductoVentaForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("ventas:producto_list")
    return render(request, "ventas/producto_form.html",
                  {"form": form, "titulo": "Editar Producto"})


# ─────────────────────────────────────────────
#  COTIZACIONES
# ─────────────────────────────────────────────
@login_required
def cotizacion_list(request):
    q      = request.GET.get("q", "")
    estado = request.GET.get("estado", "")
    qs     = Cotizacion.objects.select_related("cliente")
    if q:
        qs = qs.filter(
            Q(numero__icontains=q) |
            Q(cliente__razon_social__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, "ventas/cotizacion_list.html", {
        "cotizaciones": qs, "q": q, "estado": estado,
        "estados": Cotizacion.ESTADO_CHOICES,
    })


@login_required
def cotizacion_create(request):
    form = CotizacionForm(request.POST or None)
    if form.is_valid():
        cot = form.save(commit=False)
        cot.numero     = Cotizacion.generar_numero()
        cot.creado_por = request.user
        cot.save()
        messages.success(request, f"Cotización {cot.numero} creada.")
        return redirect("ventas:cotizacion_detail", pk=cot.pk)
    return render(request, "ventas/cotizacion_form.html",
                  {"form": form, "titulo": "Nueva Cotización"})


@login_required
def cotizacion_detail(request, pk):
    cot      = get_object_or_404(Cotizacion, pk=pk)
    detalles = cot.detalles.select_related("producto").all()
    det_form = DetalleCotizacionForm()
    return render(request, "ventas/cotizacion_detail.html", {
        "cot": cot, "detalles": detalles, "det_form": det_form,
    })


@login_required
def cotizacion_edit(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado not in ["borrador"]:
        messages.error(request, "Solo se pueden editar cotizaciones en Borrador.")
        return redirect("ventas:cotizacion_detail", pk=pk)
    form = CotizacionForm(request.POST or None, instance=cot)
    if form.is_valid():
        form.save()
        cot.calcular_totales()
        messages.success(request, "Cotización actualizada.")
        return redirect("ventas:cotizacion_detail", pk=pk)
    return render(request, "ventas/cotizacion_form.html",
                  {"form": form, "titulo": "Editar Cotización", "cot": cot})


@login_required
def cotizacion_agregar_item(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado != "borrador":
        messages.error(request, "Solo se pueden agregar ítems en Borrador.")
        return redirect("ventas:cotizacion_detail", pk=pk)
    form = DetalleCotizacionForm(request.POST)
    if form.is_valid():
        det = form.save(commit=False)
        det.cotizacion = cot
        det.save()
        cot.calcular_totales()
        messages.success(request, f"Ítem '{det.producto}' agregado.")
    else:
        messages.error(request, f"Error: {form.errors}")
    return redirect("ventas:cotizacion_detail", pk=pk)


@login_required
def cotizacion_eliminar_item(request, pk, dpk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    det = get_object_or_404(DetalleCotizacion, pk=dpk, cotizacion=cot)
    if request.method == "POST":
        det.delete()
        cot.calcular_totales()
        messages.warning(request, "Ítem eliminado.")
    return redirect("ventas:cotizacion_detail", pk=pk)


@login_required
def cotizacion_enviar(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado == "borrador" and cot.detalles.exists():
        cot.estado = "enviada"
        cot.save()
        messages.success(request, "Cotización enviada al cliente.")
    else:
        messages.error(request, "Debe tener ítems y estar en Borrador.")
    return redirect("ventas:cotizacion_detail", pk=pk)


@login_required
def cotizacion_aceptar(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado == "enviada":
        cot.estado = "aceptada"
        cot.save()
        messages.success(request, "Cotización aceptada.")
    return redirect("ventas:cotizacion_detail", pk=pk)


@login_required
def cotizacion_rechazar(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado in ["enviada", "borrador"]:
        cot.estado = "rechazada"
        cot.save()
        messages.warning(request, "Cotización rechazada.")
    return redirect("ventas:cotizacion_detail", pk=pk)


@login_required
def cotizacion_convertir_pedido(request, pk):
    cot = get_object_or_404(Cotizacion, pk=pk)
    if cot.estado != "aceptada":
        messages.error(request, "La cotización debe estar Aceptada.")
        return redirect("ventas:cotizacion_detail", pk=pk)
    if hasattr(cot, "pedido"):
        messages.warning(request, "Esta cotización ya fue convertida a pedido.")
        return redirect("ventas:pedido_detail", pk=cot.pedido.pk)

    # Crear pedido desde cotización
    pedido = Pedido.objects.create(
        numero      = Pedido.generar_numero(),
        cliente     = cot.cliente,
        cotizacion  = cot,
        fecha_pedido= timezone.now().date(),
        descuento_pct= cot.descuento_pct,
        impuesto_pct = cot.impuesto_pct,
        creado_por  = request.user,
    )
    for d in cot.detalles.all():
        DetallePedido.objects.create(
            pedido          = pedido,
            producto        = d.producto,
            descripcion     = d.descripcion,
            cantidad        = d.cantidad,
            precio_unitario = d.precio_unitario,
            descuento_pct   = d.descuento_pct,
        )
    pedido.calcular_totales()
    cot.estado = "convertida"
    cot.save()
    messages.success(request, f"Pedido {pedido.numero} creado desde cotización.")
    return redirect("ventas:pedido_detail", pk=pedido.pk)


# ─────────────────────────────────────────────
#  PEDIDOS
# ─────────────────────────────────────────────
@login_required
def pedido_list(request):
    q      = request.GET.get("q", "")
    estado = request.GET.get("estado", "")
    qs     = Pedido.objects.select_related("cliente")
    if q:
        qs = qs.filter(
            Q(numero__icontains=q) |
            Q(cliente__razon_social__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, "ventas/pedido_list.html", {
        "pedidos": qs, "q": q, "estado": estado,
        "estados": Pedido.ESTADO_CHOICES,
    })


@login_required
def pedido_create(request):
    form = PedidoForm(request.POST or None)
    if form.is_valid():
        ped = form.save(commit=False)
        ped.numero     = Pedido.generar_numero()
        ped.creado_por = request.user
        if not ped.dias_credito and ped.cliente.dias_credito:
            ped.dias_credito = ped.cliente.dias_credito
        ped.save()
        messages.success(request, f"Pedido {ped.numero} creado.")
        return redirect("ventas:pedido_detail", pk=ped.pk)
    return render(request, "ventas/pedido_form.html",
                  {"form": form, "titulo": "Nuevo Pedido"})


@login_required
def pedido_detail(request, pk):
    pedido   = get_object_or_404(Pedido, pk=pk)
    detalles = pedido.detalles.select_related("producto").all()
    det_form = DetallePedidoForm()
    despachos = pedido.despachos.order_by("-fecha_despacho")
    return render(request, "ventas/pedido_detail.html", {
        "pedido": pedido, "detalles": detalles,
        "det_form": det_form, "despachos": despachos,
    })


@login_required
def pedido_edit(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.estado not in ["borrador"]:
        messages.error(request, "Solo se pueden editar pedidos en Borrador.")
        return redirect("ventas:pedido_detail", pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    if form.is_valid():
        form.save()
        pedido.calcular_totales()
        messages.success(request, "Pedido actualizado.")
        return redirect("ventas:pedido_detail", pk=pk)
    return render(request, "ventas/pedido_form.html",
                  {"form": form, "titulo": "Editar Pedido", "pedido": pedido})


@login_required
def pedido_agregar_item(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.estado != "borrador":
        messages.error(request, "Solo se pueden agregar ítems en Borrador.")
        return redirect("ventas:pedido_detail", pk=pk)
    form = DetallePedidoForm(request.POST)
    if form.is_valid():
        det = form.save(commit=False)
        det.pedido = pedido
        det.save()
        pedido.calcular_totales()
        messages.success(request, f"Ítem '{det.producto}' agregado.")
    else:
        messages.error(request, f"Error: {form.errors}")
    return redirect("ventas:pedido_detail", pk=pk)


@login_required
def pedido_eliminar_item(request, pk, dpk):
    pedido = get_object_or_404(Pedido, pk=pk)
    det    = get_object_or_404(DetallePedido, pk=dpk, pedido=pedido)
    if request.method == "POST":
        det.delete()
        pedido.calcular_totales()
        messages.warning(request, "Ítem eliminado.")
    return redirect("ventas:pedido_detail", pk=pk)


@login_required
def pedido_confirmar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.estado == "borrador" and pedido.detalles.exists():
        pedido.estado       = "confirmado"
        pedido.aprobado_por = request.user
        pedido.save()
        messages.success(request, "Pedido confirmado.")
    else:
        messages.error(request, "El pedido debe tener ítems y estar en Borrador.")
    return redirect("ventas:pedido_detail", pk=pk)


@login_required
def pedido_en_proceso(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.estado == "confirmado":
        pedido.estado = "en_proceso"
        pedido.save()
        messages.success(request, "Pedido marcado en proceso.")
    return redirect("ventas:pedido_detail", pk=pk)


@login_required
def pedido_anular(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == "POST":
        if pedido.estado not in ["entregado", "facturado", "anulado"]:
            pedido.estado = "anulado"
            pedido.save()
            messages.warning(request, "Pedido anulado.")
        else:
            messages.error(request, "No se puede anular este pedido.")
    return redirect("ventas:pedido_detail", pk=pk)


# ─────────────────────────────────────────────
#  DESPACHOS
# ─────────────────────────────────────────────
@login_required
def despacho_list(request):
    qs = Despacho.objects.select_related("pedido__cliente").order_by("-fecha_despacho")
    return render(request, "ventas/despacho_list.html", {"despachos": qs})


@login_required
def despacho_create(request, pedido_pk):
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    if pedido.estado not in ["confirmado", "en_proceso", "despachado"]:
        messages.error(request, "El pedido debe estar Confirmado o En Proceso.")
        return redirect("ventas:pedido_detail", pk=pedido_pk)
    form = DespachoForm(request.POST or None)
    if form.is_valid():
        desp = form.save(commit=False)
        desp.pedido        = pedido
        desp.numero        = Despacho.generar_numero()
        desp.despachado_por= request.user
        desp.save()
        pedido.estado = "despachado"
        pedido.save()
        messages.success(request, f"Despacho {desp.numero} creado.")
        return redirect("ventas:despacho_detail", pk=desp.pk)
    return render(request, "ventas/despacho_form.html",
                  {"form": form, "pedido": pedido})


@login_required
def despacho_detail(request, pk):
    desp     = get_object_or_404(Despacho, pk=pk)
    detalles = desp.detalles.select_related("detalle_pedido__producto").all()
    det_form = DetalleDespachoForm()
    det_form.fields["detalle_pedido"].queryset = desp.pedido.detalles.select_related("producto")
    return render(request, "ventas/despacho_detail.html", {
        "desp": desp, "detalles": detalles, "det_form": det_form,
    })


@login_required
def despacho_agregar_item(request, pk):
    desp = get_object_or_404(Despacho, pk=pk)
    form = DetalleDespachoForm(request.POST)
    form.fields["detalle_pedido"].queryset = desp.pedido.detalles.select_related("producto")
    if form.is_valid():
        det = form.save(commit=False)
        det.despacho = desp
        det.save()
        # Actualizar cantidad despachada en el detalle del pedido
        det_ped = det.detalle_pedido
        det_ped.cantidad_despachada += det.cantidad_despachada
        det_ped.save()
        # Verificar si todo está despachado
        pendiente = any(d.pendiente_despachar > 0 for d in desp.pedido.detalles.all())
        if not pendiente:
            desp.pedido.estado = "entregado"
            desp.pedido.save()
        messages.success(request, "Ítem de despacho registrado.")
    else:
        messages.error(request, f"Error: {form.errors}")
    return redirect("ventas:despacho_detail", pk=pk)


@login_required
def despacho_entregar(request, pk):
    desp = get_object_or_404(Despacho, pk=pk)
    if desp.estado != "entregado":
        desp.estado = "entregado"
        desp.save()
        desp.pedido.estado = "entregado"
        desp.pedido.save()
        messages.success(request, "Despacho marcado como entregado.")
    return redirect("ventas:despacho_detail", pk=pk)

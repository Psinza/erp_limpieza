# apps/compras/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import (
    Proveedor, CategoriaProveedor,
    OrdenCompra, ProductoCompra, DetalleOrdenCompra, RecepcionCompra,
)
from .forms import (
    ProveedorForm, CategoriaProveedorForm,
    OrdenCompraForm, DetalleOrdenCompraForm,
    RecepcionCompraForm, DetalleRecepcionForm,
    ProductoCompraForm,
)


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
@login_required
def dashboard_compras(request):
    total_proveedores   = Proveedor.objects.filter(estado="activo").count()
    ordenes_pendientes  = OrdenCompra.objects.filter(estado="pendiente").count()
    total_mes           = (
        OrdenCompra.objects
        .filter(
            fecha_emision__month=timezone.now().month,
            fecha_emision__year=timezone.now().year,
        )
        .exclude(estado="anulada")
        .aggregate(Sum("total"))["total__sum"] or 0
    )
    ultimas_ordenes     = OrdenCompra.objects.select_related("proveedor").order_by("-fecha_emision")[:6]

    return render(request, "compras/dashboard_compras.html", {
        "total_proveedores":  total_proveedores,
        "ordenes_pendientes": ordenes_pendientes,
        "total_mes":          total_mes,
        "ultimas_ordenes":    ultimas_ordenes,
    })


# ─────────────────────────────────────────────
#  CATEGORÍAS PROVEEDOR
# ─────────────────────────────────────────────
@login_required
def categoria_proveedor_list(request):
    cats = CategoriaProveedor.objects.annotate(num=Count("proveedores"))
    return render(request, "compras/categoria_proveedor_list.html", {"categorias": cats})


@login_required
def categoria_proveedor_create(request):
    form = CategoriaProveedorForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoría creada.")
        return redirect("compras:categoria_proveedor_list")
    return render(request, "compras/categoria_proveedor_form.html",
                  {"form": form, "titulo": "Nueva Categoría de Proveedor"})


@login_required
def categoria_proveedor_edit(request, pk):
    obj  = get_object_or_404(CategoriaProveedor, pk=pk)
    form = CategoriaProveedorForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Categoría actualizada.")
        return redirect("compras:categoria_proveedor_list")
    return render(request, "compras/categoria_proveedor_form.html",
                  {"form": form, "titulo": "Editar Categoría"})


# ─────────────────────────────────────────────
#  PROVEEDORES
# ─────────────────────────────────────────────
@login_required
def proveedor_list(request):
    q      = request.GET.get("q", "")
    estado = request.GET.get("estado", "")
    cat    = request.GET.get("categoria", "")

    qs = Proveedor.objects.select_related("categoria")
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

    categorias = CategoriaProveedor.objects.all()
    return render(request, "compras/proveedor_list.html", {
        "proveedores": qs, "categorias": categorias,
        "q": q, "estado": estado, "cat": cat,
    })


@login_required
def proveedor_detail(request, pk):
    prov      = get_object_or_404(Proveedor, pk=pk)
    contactos = prov.contactos.all()
    ordenes   = prov.ordenes.order_by("-fecha_emision")[:10]
    totales   = prov.ordenes.exclude(estado="anulada").aggregate(
        total_comprado=Sum("total"), num_ordenes=Count("id")
    )
    return render(request, "compras/proveedor_detail.html", {
        "prov": prov, "contactos": contactos,
        "ordenes": ordenes, "totales": totales,
    })


@login_required
def proveedor_create(request):
    form = ProveedorForm(request.POST or None)
    if form.is_valid():
        prov = form.save()
        messages.success(request, f"Proveedor '{prov.razon_social}' creado.")
        return redirect("compras:proveedor_detail", pk=prov.pk)
    return render(request, "compras/proveedor_form.html",
                  {"form": form, "titulo": "Nuevo Proveedor"})


@login_required
def proveedor_edit(request, pk):
    prov = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=prov)
    if form.is_valid():
        form.save()
        messages.success(request, "Proveedor actualizado.")
        return redirect("compras:proveedor_detail", pk=prov.pk)
    return render(request, "compras/proveedor_form.html",
                  {"form": form, "titulo": "Editar Proveedor", "prov": prov})


@login_required
def proveedor_contacto_add(request, pk):
    prov = get_object_or_404(Proveedor, pk=pk)
    form = ContactoProveedorForm(request.POST or None)
    if form.is_valid():
        c = form.save(commit=False)
        c.proveedor = prov
        c.save()
        messages.success(request, "Contacto agregado.")
        return redirect("compras:proveedor_detail", pk=pk)
    return render(request, "compras/contacto_form.html",
                  {"form": form, "prov": prov})


@login_required
def proveedor_contacto_delete(request, pk, cpk):
    contacto = get_object_or_404(ContactoProveedor, pk=cpk, proveedor__pk=pk)
    if request.method == "POST":
        contacto.delete()
        messages.warning(request, "Contacto eliminado.")
    return redirect("compras:proveedor_detail", pk=pk)


# ─────────────────────────────────────────────
#  PRODUCTOS DE COMPRA
# ─────────────────────────────────────────────
@login_required
def producto_list(request):
    q   = request.GET.get("q", "")
    cat = request.GET.get("categoria", "")
    qs  = ProductoCompra.objects.select_related("categoria")
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    if cat:
        qs = qs.filter(categoria__id=cat)
    categorias = CategoriaProductoCompra.objects.all()
    return render(request, "compras/producto_list.html", {
        "productos": qs, "categorias": categorias, "q": q, "cat": cat,
    })


@login_required
def producto_create(request):
    form = ProductoCompraForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Producto creado.")
        return redirect("compras:producto_list")
    return render(request, "compras/producto_form.html",
                  {"form": form, "titulo": "Nuevo Producto"})


@login_required
def producto_edit(request, pk):
    obj  = get_object_or_404(ProductoCompra, pk=pk)
    form = ProductoCompraForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("compras:producto_list")
    return render(request, "compras/producto_form.html",
                  {"form": form, "titulo": "Editar Producto"})


# ─────────────────────────────────────────────
#  ÓRDENES DE COMPRA
# ─────────────────────────────────────────────
@login_required
def orden_list(request):
    q      = request.GET.get("q", "")
    estado = request.GET.get("estado", "")
    qs     = OrdenCompra.objects.select_related("proveedor")
    if q:
        qs = qs.filter(
            Q(numero__icontains=q) |
            Q(proveedor__razon_social__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, "compras/orden_list.html", {
        "ordenes": qs, "q": q, "estado": estado,
        "estados": OrdenCompra.ESTADO_CHOICES,
    })


@login_required
def orden_create(request):
    form = OrdenCompraForm(request.POST or None)
    if form.is_valid():
        orden = form.save()
        messages.success(request, f"Orden #{orden.id} creada.")
        return redirect("compras:orden_detail", pk=orden.pk)
    return render(request, "compras/orden_form.html",
                  {"form": form, "titulo": "Nueva Orden de Compra"})


@login_required
def orden_detail(request, pk):
    orden    = get_object_or_404(OrdenCompra, pk=pk)
    detalles = orden.detalles.select_related("producto").all()
    det_form = DetalleOrdenCompraForm()
    recepciones = orden.recepciones.order_by("-fecha_recepcion")
    return render(request, "compras/orden_detail.html", {
        "orden": orden, "detalles": detalles,
        "det_form": det_form, "recepciones": recepciones,
    })


@login_required
def orden_edit(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if orden.estado not in ["borrador"]:
        messages.error(request, "Solo se pueden editar órdenes en Borrador.")
        return redirect("compras:orden_detail", pk=pk)
    form = OrdenCompraForm(request.POST or None, instance=orden)
    if form.is_valid():
        form.save()
        orden.calcular_totales()
        messages.success(request, "Orden actualizada.")
        return redirect("compras:orden_detail", pk=pk)
    return render(request, "compras/orden_form.html",
                  {"form": form, "titulo": "Editar Orden", "orden": orden})


@login_required
def orden_agregar_detalle(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if orden.estado != "borrador":
        messages.error(request, "Solo se puede agregar ítems en estado Borrador.")
        return redirect("compras:orden_detail", pk=pk)
    form = DetalleOrdenCompraForm(request.POST)
    if form.is_valid():
        det       = form.save(commit=False)
        det.orden = orden
        det.save()
        orden.calcular_totales()
        messages.success(request, f"Ítem '{det.producto}' agregado.")
    else:
        messages.error(request, f"Error: {form.errors}")
    return redirect("compras:orden_detail", pk=pk)


@login_required
def orden_eliminar_detalle(request, pk, dpk):
    orden  = get_object_or_404(OrdenCompra, pk=pk)
    detalle= get_object_or_404(DetalleOrdenCompra, pk=dpk, orden=orden)
    if request.method == "POST":
        detalle.delete()
        orden.calcular_totales()
        messages.warning(request, "Ítem eliminado.")
    return redirect("compras:orden_detail", pk=pk)


@login_required
def orden_enviar(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if orden.estado == "borrador" and orden.detalles.exists():
        orden.estado = "enviada"
        orden.save()
        messages.success(request, "Orden enviada al proveedor.")
    else:
        messages.error(request, "La orden debe tener ítems y estar en Borrador.")
    return redirect("compras:orden_detail", pk=pk)


@login_required
def orden_confirmar(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if orden.estado == "enviada":
        orden.estado      = "confirmada"
        orden.aprobado_por= request.user
        orden.save()
        messages.success(request, "Orden confirmada.")
    else:
        messages.error(request, "La orden debe estar en estado Enviada.")
    return redirect("compras:orden_detail", pk=pk)


@login_required
def orden_anular(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if request.method == "POST":
        if orden.estado not in ["completada", "anulada"]:
            orden.estado = "anulada"
            orden.save()
            messages.warning(request, "Orden anulada.")
        else:
            messages.error(request, "No se puede anular esta orden.")
    return redirect("compras:orden_detail", pk=pk)


# ─────────────────────────────────────────────
#  RECEPCIONES
# ─────────────────────────────────────────────
@login_required
def recepcion_list(request):
    qs = RecepcionCompra.objects.select_related("orden__proveedor").order_by("-fecha_recepcion")
    return render(request, "compras/recepcion_list.html", {"recepciones": qs})


@login_required
def recepcion_create(request, orden_pk):
    orden = get_object_or_404(OrdenCompra, pk=orden_pk)
    if orden.estado not in ["confirmada", "recibida"]:
        messages.error(request, "La orden debe estar Confirmada para registrar recepción.")
        return redirect("compras:orden_detail", pk=orden_pk)

    form = RecepcionCompraForm(request.POST or None)
    if form.is_valid():
        rec = form.save(commit=False)
        rec.orden        = orden
        rec.numero       = RecepcionCompra.generar_numero()
        rec.recibido_por = request.user
        rec.save()
        # Actualizar estado de la orden
        orden.estado = "recibida"
        orden.save()
        messages.success(request, f"Recepción {rec.numero} creada.")
        return redirect("compras:recepcion_detail", pk=rec.pk)
    return render(request, "compras/recepcion_form.html",
                  {"form": form, "orden": orden})


@login_required
def recepcion_detail(request, pk):
    rec      = get_object_or_404(RecepcionCompra, pk=pk)
    detalles = rec.detalles.select_related("detalle_orden__producto").all()
    det_form = DetalleRecepcionForm()
    # Filtrar solo detalles de la orden correspondiente
    det_form.fields["detalle_orden"].queryset = rec.orden.detalles.select_related("producto")
    return render(request, "compras/recepcion_detail.html", {
        "rec": rec, "detalles": detalles, "det_form": det_form,
    })


@login_required
def recepcion_agregar_detalle(request, pk):
    rec = get_object_or_404(RecepcionCompra, pk=pk)
    form = DetalleRecepcionForm(request.POST)
    form.fields["detalle_orden"].queryset = rec.orden.detalles.select_related("producto")
    if form.is_valid():
        det           = form.save(commit=False)
        det.recepcion = rec
        det.save()
        # Actualizar cantidad recibida en el detalle de la orden
        det_orden = det.detalle_orden
        det_orden.cantidad_recibida += det.cantidad_aceptada
        det_orden.save()
        # Verificar si la orden está completada
        orden    = rec.orden
        pendiente = any(
            d.pendiente_recibir > 0 for d in orden.detalles.all()
        )
        if not pendiente:
            orden.estado = "completada"
            orden.save()
        messages.success(request, "Ítem recibido registrado.")
    else:
        messages.error(request, f"Error: {form.errors}")
    return redirect("compras:recepcion_detail", pk=pk)


@login_required
def recepcion_aprobar(request, pk):
    rec = get_object_or_404(RecepcionCompra, pk=pk)
    if rec.estado == "pendiente":
        rec.estado = "aprobada"
        rec.save()
        messages.success(request, "Recepción aprobada.")
    return redirect("compras:recepcion_detail", pk=pk)

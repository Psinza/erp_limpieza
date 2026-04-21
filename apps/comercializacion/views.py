from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CategoriaComercial, InformacionComercial, ListaPrecio, ItemPrecio
from .forms import CategoriaComercialForm, InformacionComercialForm, ListaPrecioForm, ItemPrecioForm

@login_required
def dashboard_comercializacion(request):
    """Dashboard de comercialización."""
    categorias = CategoriaComercial.objects.all()
    productos = InformacionComercial.objects.select_related('producto', 'categoria').all()
    listas = ListaPrecio.objects.filter(activa=True)
    
    context = {
        'categorias': categorias,
        'productos': productos,
        'listas': listas,
    }
    return render(request, 'comercializacion/dashboard.html', context)

# Categorías
@login_required
def categoria_list(request):
    categorias = CategoriaComercial.objects.all()
    return render(request, 'comercializacion/categoria_list.html', {'categorias': categorias})

@login_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaComercialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('comercializacion:categoria_list')
    else:
        form = CategoriaComercialForm()
    return render(request, 'comercializacion/categoria_form.html', {'form': form, 'title': 'Crear Categoría'})

@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(CategoriaComercial, pk=pk)
    if request.method == 'POST':
        form = CategoriaComercialForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('comercializacion:categoria_list')
    else:
        form = CategoriaComercialForm(instance=categoria)
    return render(request, 'comercializacion/categoria_form.html', {'form': form, 'title': 'Editar Categoría'})

@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(CategoriaComercial, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
        return redirect('comercializacion:categoria_list')
    return render(request, 'comercializacion/categoria_confirm_delete.html', {'categoria': categoria})

# Información Comercial
@login_required
def producto_comercial_list(request):
    productos = InformacionComercial.objects.select_related('producto', 'categoria').all()
    return render(request, 'comercializacion/producto_comercial_list.html', {'productos': productos})

@login_required
def producto_comercial_create(request):
    if request.method == 'POST':
        form = InformacionComercialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información comercial creada exitosamente.')
            return redirect('comercializacion:producto_comercial_list')
    else:
        form = InformacionComercialForm()
    return render(request, 'comercializacion/producto_comercial_form.html', {'form': form, 'title': 'Crear Información Comercial'})

@login_required
def producto_comercial_update(request, pk):
    info = get_object_or_404(InformacionComercial, pk=pk)
    if request.method == 'POST':
        form = InformacionComercialForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información comercial actualizada exitosamente.')
            return redirect('comercializacion:producto_comercial_list')
    else:
        form = InformacionComercialForm(instance=info)
    return render(request, 'comercializacion/producto_comercial_form.html', {'form': form, 'title': 'Editar Información Comercial'})

@login_required
def producto_comercial_delete(request, pk):
    info = get_object_or_404(InformacionComercial, pk=pk)
    if request.method == 'POST':
        info.delete()
        messages.success(request, 'Información comercial eliminada exitosamente.')
        return redirect('comercializacion:producto_comercial_list')
    return render(request, 'comercializacion/producto_comercial_confirm_delete.html', {'info': info})

# Listas de Precio
@login_required
def lista_precio_list(request):
    listas = ListaPrecio.objects.all()
    return render(request, 'comercializacion/lista_precio_list.html', {'listas': listas})

@login_required
def lista_precio_create(request):
    if request.method == 'POST':
        form = ListaPrecioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lista de precios creada exitosamente.')
            return redirect('comercializacion:lista_precio_list')
    else:
        form = ListaPrecioForm()
    return render(request, 'comercializacion/lista_precio_form.html', {'form': form, 'title': 'Crear Lista de Precios'})

@login_required
def lista_precio_update(request, pk):
    lista = get_object_or_404(ListaPrecio, pk=pk)
    if request.method == 'POST':
        form = ListaPrecioForm(request.POST, instance=lista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lista de precios actualizada exitosamente.')
            return redirect('comercializacion:lista_precio_list')
    else:
        form = ListaPrecioForm(instance=lista)
    return render(request, 'comercializacion/lista_precio_form.html', {'form': form, 'title': 'Editar Lista de Precios'})

@login_required
def lista_precio_delete(request, pk):
    lista = get_object_or_404(ListaPrecio, pk=pk)
    if request.method == 'POST':
        lista.delete()
        messages.success(request, 'Lista de precios eliminada exitosamente.')
        return redirect('comercializacion:lista_precio_list')
    return render(request, 'comercializacion/lista_precio_confirm_delete.html', {'lista': lista})

# Items de Precio
@login_required
def item_precio_list(request, lista_id):
    lista = get_object_or_404(ListaPrecio, pk=lista_id)
    items = ItemPrecio.objects.filter(lista=lista).select_related('producto')
    return render(request, 'comercializacion/item_precio_list.html', {'lista': lista, 'items': items})

@login_required
def item_precio_create(request, lista_id):
    lista = get_object_or_404(ListaPrecio, pk=lista_id)
    if request.method == 'POST':
        form = ItemPrecioForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.lista = lista
            item.save()
            messages.success(request, 'Precio agregado exitosamente.')
            return redirect('comercializacion:item_precio_list', lista_id=lista_id)
    else:
        form = ItemPrecioForm()
    return render(request, 'comercializacion/item_precio_form.html', {'form': form, 'lista': lista, 'title': 'Agregar Precio'})

@login_required
def item_precio_update(request, pk):
    item = get_object_or_404(ItemPrecio, pk=pk)
    if request.method == 'POST':
        form = ItemPrecioForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Precio actualizado exitosamente.')
            return redirect('comercializacion:item_precio_list', lista_id=item.lista_id)
    else:
        form = ItemPrecioForm(instance=item)
    return render(request, 'comercializacion/item_precio_form.html', {'form': form, 'lista': item.lista, 'title': 'Editar Precio'})

@login_required
def item_precio_delete(request, pk):
    item = get_object_or_404(ItemPrecio, pk=pk)
    lista_id = item.lista_id
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Precio eliminado exitosamente.')
        return redirect('comercializacion:item_precio_list', lista_id=lista_id)
    return render(request, 'comercializacion/item_precio_confirm_delete.html', {'item': item})
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import ActivoFijo
from .forms import ActivoFijoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.db.models import Q # Importar Q para búsquedas complejas

class ActivoFijoListView(LoginRequiredMixin, ListView):
    model = ActivoFijo
    template_name = 'activos_fijos/activo_list.html'
    context_object_name = 'activos'
    ordering = ['codigo']
    paginate_by = 10  # Muestra 10 activos por página

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(codigo__icontains=query) | Q(nombre__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '') # Para mantener el valor de búsqueda en el input
        return context

class ActivoFijoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ActivoFijo
    form_class = ActivoFijoForm
    template_name = 'activos_fijos/activo_form.html'
    success_url = reverse_lazy('activos_fijos:activo_list')
    success_message = "¡El activo '%(nombre)s' se ha creado correctamente!"

class ActivoFijoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ActivoFijo
    form_class = ActivoFijoForm
    template_name = 'activos_fijos/activo_form.html'
    success_url = reverse_lazy('activos_fijos:activo_list')
    success_message = "¡El activo '%(nombre)s' se ha actualizado correctamente!"

class ActivoFijoDeleteView(LoginRequiredMixin, DeleteView):
    model = ActivoFijo
    template_name = 'activos_fijos/activo_confirm_delete.html'
    success_url = reverse_lazy('activos_fijos:activo_list')
    
    def post(self, request, *args, **kwargs):
        messages.success(request, "El activo ha sido eliminado correctamente.")
        return super().post(request, *args, **kwargs)

def exportar_activos_a_excel(request):
    try:
        from openpyxl import Workbook
    except ModuleNotFoundError:
        messages.error(request, 'La exportación a Excel requiere el paquete openpyxl. Instálalo con pip install openpyxl.')
        return HttpResponseRedirect(reverse_lazy('activos_fijos:activo_list'))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="activos_fijos.xlsx"'

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Activos Fijos"

    # Encabezados
    headers = ["Código", "Nombre", "Fecha Adquisición", "Valor Compra", "Vida Útil (Meses)"]
    sheet.append(headers)

    # Datos
    for activo in ActivoFijo.objects.all().order_by('codigo'):
        sheet.append([activo.codigo, activo.nombre, activo.fecha_adquisicion, activo.valor_compra, activo.vida_util_anios])

    workbook.save(response)
    return response

def reporte_depreciacion(request):
    activos = ActivoFijo.objects.all()
    total_valor_compra = sum(activo.valor_compra for activo in activos)
    total_depreciacion_acumulada = sum(activo.depreciacion_acumulada for activo in activos)
    total_valor_libro = sum(activo.valor_libro for activo in activos)
    
    context = {
        'activos': activos,
        'total_valor_compra': total_valor_compra,
        'total_depreciacion_acumulada': total_depreciacion_acumulada,
        'total_valor_libro': total_valor_libro,
    }
    return render(request, 'activos_fijos/reporte_depreciacion.html', context)
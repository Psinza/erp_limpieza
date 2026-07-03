from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import ActivoFijo
from .forms import ActivoFijoForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from openpyxl import Workbook
from django.db.models import Q

class ActivoFijoListView(LoginRequiredMixin, ListView):
    model = ActivoFijo
    template_name = 'activos_fijos/activo_list.html'
    context_object_name = 'activos'
    ordering = ['codigo']
    paginate_by = 10

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
        context['q'] = self.request.GET.get('q', '')
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
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="activos_fijos.xlsx"'
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Activos Fijos"
    headers = ["Código", "Nombre", "Fecha Adquisición", "Valor Compra", "Vida Útil (Meses)"]
    sheet.append(headers)
    for activo in ActivoFijo.objects.all().order_by('codigo'):
        sheet.append([activo.codigo, activo.nombre, activo.fecha_adquisicion, activo.valor_compra, activo.vida_util_meses])
    workbook.save(response)
    return response
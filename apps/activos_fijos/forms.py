from django import forms
from .models import ActivoFijo, AsignacionActivo, MantenimientoActivo

class ActivoFijoForm(forms.ModelForm):
    class Meta:
        model = ActivoFijo
        fields = [
            'codigo', 'serial', 'nombre', 'descripcion', 'modelo', 'anio_fabricacion', 'categoria', 
            'fecha_adquisicion', 'valor_compra', 'valor_residual', 
            'vida_util_anios', 'metodo_depreciacion', 'estado', 
            'ubicacion', 'responsable'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: BM-0001 (Bien Nacional)'}),
            'serial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Serial de Fábrica'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre descriptivo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción física detallada'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Modelo del equipo'}),
            'anio_fabricacion': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2020'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_residual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vida_util_anios': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_depreciacion': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(choices=[('Bueno', 'Bueno'), ('Regular', 'Regular'), ('Malo', 'Malo'), ('Chatarra', 'Chatarra')], attrs={'class': 'form-select'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación física actual'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

class AsignacionActivoForm(forms.ModelForm):
    class Meta:
        model = AsignacionActivo
        fields = ['empleado', 'departamento', 'fecha_asignacion', 'fecha_devolucion', 'estado_entrega', 'estado_devolucion', 'observaciones']
        widgets = {
            'empleado': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_asignacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_devolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_devolucion': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MantenimientoActivoForm(forms.ModelForm):
    class Meta:
        model = MantenimientoActivo
        fields = ['fecha_mantenimiento', 'tipo', 'descripcion', 'proveedor', 'costo', 'proximo_mantenimiento']
        widgets = {
            'fecha_mantenimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proximo_mantenimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
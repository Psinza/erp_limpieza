from django import forms
from .models import Formula, OrdenProduccion, MateriaPrima, ProductoTerminado, LoteProduccion, ControlCalidad

class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        fields = ['codigo', 'nombre', 'producto', 'version', 'rendimiento', 'unidad_rendimiento', 'instrucciones', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'rendimiento': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad_rendimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'instrucciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class OrdenProduccionForm(forms.ModelForm):
    class Meta:
        model = OrdenProduccion
        fields = ['formula', 'cantidad_planificada', 'fecha_planificada', 'prioridad', 'responsable', 'observaciones']
        widgets = {
            'formula': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_planificada': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_planificada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LoteProduccionForm(forms.ModelForm):
    class Meta:
        model = LoteProduccion
        fields = ['orden', 'numero_lote', 'cantidad_producida', 'estado', 'observaciones']
        widgets = {
            'orden': forms.Select(attrs={'class': 'form-select'}),
            'numero_lote': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_producida': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ControlCalidadForm(forms.ModelForm):
    # Añadimos la cantidad final del lote al formulario de QC para que se registre en este paso
    cantidad_final_lote = forms.DecimalField(
        max_digits=12, decimal_places=2,
        label="Cantidad Final Producida",
        help_text="Cantidad real de producto terminado obtenida en este lote.",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    class Meta:
        model = ControlCalidad
        fields = [
            'ph', 'viscosidad', 'densidad', 'color', 'olor', 'aspecto',
            'observaciones', 'aprobado', 'inspector'
        ]
        widgets = {
            'ph': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'viscosidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'densidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'olor': forms.TextInput(attrs={'class': 'form-control'}),
            'aspecto': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'aprobado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'inspector': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'ph': 'pH del Lote',
            'viscosidad': 'Viscosidad (cP)',
            'densidad': 'Densidad (g/cm³)',
            'color': 'Color Observado',
            'olor': 'Olor Observado',
            'aspecto': 'Aspecto Físico',
            'observaciones': 'Observaciones Adicionales',
            'aprobado': 'Lote Aprobado',
            'inspector': 'Nombre del Inspector',
        }

    def __init__(self, *args, **kwargs):
        lote_instance = kwargs.pop('lote_instance', None)
        super().__init__(*args, **kwargs)
        if lote_instance:
            # Precargar la cantidad_final_lote si ya existe en el lote
            self.fields['cantidad_final_lote'].initial = lote_instance.cantidad_final

    def save(self, commit=True):
        control_calidad = super().save(commit=False)
        if commit:
            control_calidad.save()
            # Actualizar la cantidad_final del lote con el valor del formulario
            lote = control_calidad.lote
            lote.cantidad_final = self.cleaned_data['cantidad_final_lote']
            lote.save(update_fields=['cantidad_final']) # Guardar solo el campo modificado
        return control_calidad

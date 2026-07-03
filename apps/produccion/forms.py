from django import forms
from .models import Formula, LineaFormula, OrdenProduccion, ControlCalidad, ProductoTerminado

CTR = {"class": "form-control"}
SEL = {"class": "form-select"}
NUM = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}
TXT = {"class": "form-control", "rows": 3}

class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        fields = ['codigo', 'nombre', 'producto', 'version', 'rendimiento', 'unidad_rendimiento', 'procedimiento', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs=CTR),
            'nombre': forms.TextInput(attrs=CTR),
            'producto': forms.Select(attrs=SEL),
            'version': forms.TextInput(attrs=CTR),
            'rendimiento': forms.NumberInput(attrs=NUM),
            'unidad_rendimiento': forms.TextInput(attrs=CTR),
            'procedimiento': forms.Textarea(attrs=TXT),
            'estado': forms.Select(attrs=SEL),
        }

class OrdenProduccionForm(forms.ModelForm):
    class Meta:
        model = OrdenProduccion
        fields = ['formula', 'lote_numero', 'cantidad_a_producir', 'prioridad', 'fecha_planificada', 'responsable', 'observaciones']
        widgets = {
            'formula': forms.Select(attrs=SEL),
            'lote_numero': forms.TextInput(attrs=CTR),
            'cantidad_a_producir': forms.NumberInput(attrs=CTR),
            'prioridad': forms.Select(attrs=SEL),
            'fecha_planificada': forms.DateInput(attrs=DATE),
            'responsable': forms.Select(attrs=SEL),
            'observaciones': forms.Textarea(attrs=TXT),
        }

class ControlCalidadForm(forms.ModelForm):
    class Meta:
        model = ControlCalidad
        fields = [
            'ph', 'viscosidad', 'densidad', 'concentracion_activo', 
            'color', 'olor', 'aspecto', 'cumple_covenin', 'aprobado', 'inspector', 'observaciones'
        ]
        widgets = {
            'ph': forms.NumberInput(attrs=NUM),
            'viscosidad': forms.NumberInput(attrs=NUM),
            'densidad': forms.NumberInput(attrs=NUM),
            'concentracion_activo': forms.NumberInput(attrs=NUM),
            'color': forms.TextInput(attrs=CTR),
            'olor': forms.TextInput(attrs=CTR),
            'aspecto': forms.TextInput(attrs=CTR),
            'cumple_covenin': forms.CheckboxInput(attrs={"class": "form-check-input"}),
            'aprobado': forms.CheckboxInput(attrs={"class": "form-check-input"}),
            'inspector': forms.TextInput(attrs=CTR),
            'observaciones': forms.Textarea(attrs=TXT),
        }

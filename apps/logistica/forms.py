from django import forms
from .models import MovimientoInventario, Almacen
from apps.produccion.models import MateriaPrima, ProductoTerminado

CTR = {"class": "form-control"}
SEL = {"class": "form-select"}
NUM = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}
TXT = {"class": "form-control", "rows": 3}

class MovimientoInventarioForm(forms.ModelForm):
    item_tipo = forms.ChoiceField(
        choices=[('mp', 'Materia Prima'), ('pt', 'Producto Terminado')],
        widget=forms.Select(attrs=SEL),
        label="Tipo de Item"
    )
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'tipo', 'motivo', 'materia_prima', 'producto_pt', 
            'almacen_origen', 'almacen_destino', 'cantidad', 'referencia'
        ]
        widgets = {
            'tipo': forms.Select(attrs=SEL),
            'motivo': forms.Select(attrs=SEL),
            'materia_prima': forms.Select(attrs=SEL),
            'producto_pt': forms.Select(attrs=SEL),
            'almacen_origen': forms.Select(attrs=SEL),
            'almacen_destino': forms.Select(attrs=SEL),
            'cantidad': forms.NumberInput(attrs=NUM),
            'referencia': forms.TextInput(attrs=CTR),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['materia_prima'].required = False
        self.fields['producto_pt'].required = False
        self.fields['almacen_origen'].required = False
        self.fields['almacen_destino'].required = False

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'ubicacion', 'es_principal', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs=CTR),
            'ubicacion': forms.TextInput(attrs=CTR),
            'es_principal': forms.CheckboxInput(attrs={"class": "form-check-input"}),
            'activo': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
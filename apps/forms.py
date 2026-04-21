from django import forms
from .models import ActivoFijo

class ActivoFijoForm(forms.ModelForm):
    class Meta:
        model = ActivoFijo
        fields = ['codigo', 'nombre', 'fecha_adquisicion', 'valor_compra', 'vida_util_meses']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: MAQ-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del activo'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vida_util_meses': forms.NumberInput(attrs={'class': 'form-control'}),
        }
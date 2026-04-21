from django import forms
from .models import ActivoFijo

class ActivoFijoForm(forms.ModelForm):
    class Meta:
        model = ActivoFijo
        fields = ['codigo', 'nombre', 'categoria', 'fecha_adquisicion', 'valor_compra', 'valor_residual', 'vida_util_anios', 'metodo_depreciacion', 'estado', 'ubicacion', 'responsable']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: MAQ-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del activo'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_residual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vida_util_anios': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_depreciacion': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django import forms
from .models import ActivoFijo

class ActivoFijoForm(forms.ModelForm):
    class Meta:
        model = ActivoFijo
        fields = ['codigo', 'nombre', 'fecha_adquisicion', 'valor_compra', 'nro_factura', 'nro_control', 'proveedor_rif', 'vida_util_meses']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: MAQ-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del activo'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nro_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'nro_control': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor_rif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'J-12345678-9'}),
            'vida_util_meses': forms.NumberInput(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import SolicitudViatico, GastoViatico

class SolicitudViaticoForm(forms.ModelForm):
    class Meta:
        model = SolicitudViatico
        fields = [
            'empleado', 'beneficiario_nombre', 'beneficiario_cargo', 'beneficiario_departamento',
            'fecha_viaje', 'destino', 'motivo', 'monto_estimado', 'moneda', 'tasa_bcv'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'beneficiario_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo si no es empleado'}),
            'beneficiario_cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Chofer, Vendedor...'}),
            'beneficiario_departamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Logística...'}),
            'fecha_viaje': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad o sucursal'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción del viaje...'}),
            'monto_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'tasa_bcv': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
        }
        labels = {
            'monto_estimado': 'Monto estimado',
        }

class GastoViaticoForm(forms.ModelForm):
    class Meta:
        model = GastoViatico
        fields = [
            'tipo', 'descripcion', 'fecha', 'monto', 'moneda', 'tasa_bcv',
            'proveedor_rif', 'proveedor_nombre', 'nro_factura', 'nro_control',
            'es_reembolsable', 'comprobante',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'tasa_bcv': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'proveedor_rif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'J-12345678-9'}),
            'proveedor_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nro_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'nro_control': forms.TextInput(attrs={'class': 'form-control'}),
            'es_reembolsable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comprobante': forms.FileInput(attrs={'class': 'form-control'}),
        }

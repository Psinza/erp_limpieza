from django import forms
from .models import Empresa, FacturaVenta, DetalleFacturaVenta

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'nombre', 'rif', 'direccion', 'telefono', 
            'email', 'logo', 'moneda_simbolo', 
            'contribuyente_especial', 'iva_porcentaje'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: J-12345678-0'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class FacturaVentaForm(forms.ModelForm):
    class Meta:
        model = FacturaVenta
        fields = [
            'cliente', 'pedido', 'tipo_documento', 'numero_factura', 
            'numero_control', 'fecha_emision', 'fecha_vencimiento',
            'monto_igtf'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select select2'}),
            'pedido': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 00000001'}),
            'numero_control': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 00-000001'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto_igtf': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class DetalleFacturaVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleFacturaVenta
        fields = ['producto', 'descripcion', 'cantidad', 'precio_unitario', 'tipo_impuesto']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo_impuesto': forms.Select(attrs={'class': 'form-select'}),
        }
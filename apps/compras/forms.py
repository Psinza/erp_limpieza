from django import forms
from .models import OrdenCompra, FacturaCompra, DetalleFacturaCompra, ProductoCompra
from apps.facturacion.models import Proveedor
from apps.produccion.models import MateriaPrima

CTR = {"class": "form-control"}
SEL = {"class": "form-select"}
NUM = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}
TXT = {"class": "form-control", "rows": 3}

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'rif', 'direccion', 'telefono', 'email']
        widgets = {
            'razon_social': forms.TextInput(attrs=CTR),
            'rif': forms.TextInput(attrs=CTR),
            'direccion': forms.Textarea(attrs=TXT),
            'telefono': forms.TextInput(attrs=CTR),
            'email': forms.EmailInput(attrs=CTR),
        }

class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nombre', 'sku', 'categoria', 'unidad_medida', 'stock_minimo', 'costo_unitario', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs=CTR),
            'sku': forms.TextInput(attrs=CTR),
            'categoria': forms.Select(attrs=SEL),
            'unidad_medida': forms.Select(attrs=SEL),
            'stock_minimo': forms.NumberInput(attrs=NUM),
            'costo_unitario': forms.NumberInput(attrs=NUM),
            'activo': forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class ProductoCompraForm(forms.ModelForm):
    class Meta:
        model = ProductoCompra
        fields = ['nombre', 'codigo', 'descripcion', 'precio_referencia']
        widgets = {
            'nombre': forms.TextInput(attrs=CTR),
            'codigo': forms.TextInput(attrs=CTR),
            'descripcion': forms.Textarea(attrs=TXT),
            'precio_referencia': forms.NumberInput(attrs=NUM),
        }

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['proveedor', 'fecha_emision', 'estado']
        widgets = {
            'proveedor': forms.Select(attrs=SEL),
            'fecha_emision': forms.DateInput(attrs=DATE),
            'estado': forms.Select(attrs=SEL),
        }
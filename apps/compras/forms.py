from django import forms
from .models import (
    Proveedor, CategoriaProveedor, OrdenCompra, 
    ProductoCompra, DetalleOrdenCompra, RecepcionCompra, DetalleRecepcion
)

class CategoriaProveedorForm(forms.ModelForm):
    class Meta:
        model = CategoriaProveedor
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['ruc', 'razon_social', 'nombre_comercial', 'categoria', 'telefono', 'email', 'direccion', 'estado']
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductoCompraForm(forms.ModelForm):
    class Meta:
        model = ProductoCompra
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['proveedor', 'fecha_entrega', 'observaciones']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DetalleOrdenCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleOrdenCompra
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RecepcionCompraForm(forms.ModelForm):
    class Meta:
        model = RecepcionCompra
        fields = ['orden']
        widgets = {
            'orden': forms.Select(attrs={'class': 'form-select'}),
        }

class DetalleRecepcionForm(forms.ModelForm):
    class Meta:
        model = DetalleRecepcion
        fields = ['detalle_orden', 'cantidad_aceptada', 'observaciones']
        widgets = {
            'detalle_orden': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_aceptada': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django import forms
from .models import InformacionComercial, ListaPrecio, ItemPrecio, CategoriaComercial
from apps.produccion.models import ProductoTerminado
from decimal import Decimal

class CategoriaComercialForm(forms.ModelForm):
    class Meta:
        model = CategoriaComercial
        fields = ['nombre', 'descripcion', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }


class InformacionComercialForm(forms.ModelForm):
    class Meta:
        model = InformacionComercial
        fields = ['producto', 'categoria', 'nombre_comercial', 'descripcion_larga',
                  'ficha_tecnica', 'en_oferta', 'destacado']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre_comercial': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre para el catálogo'
            }),
            'descripcion_larga': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Descripción detallada para el cliente'
            }),
            'ficha_tecnica': forms.FileInput(attrs={'class': 'form-control'}),
            'en_oferta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = ProductoTerminado.objects.all()
        if not self.instance.pk:
            productos_usados = InformacionComercial.objects.values_list('producto_id', flat=True)
            qs = qs.exclude(id__in=productos_usados)
        self.fields['producto'].queryset = qs
        self.fields['producto'].empty_label = "Seleccione un producto..."


class ListaPrecioForm(forms.ModelForm):
    class Meta:
        model = ListaPrecio
        fields = ['nombre', 'descripcion', 'moneda', 'factor_ajuste', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Lista PVP, Mayorista...'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'moneda': forms.Select(
                choices=[('USD', 'Dólar (USD)'), ('EUR', 'Euro (EUR)'), ('VES', 'Bolívar (VES)')],
                attrs={'class': 'form-select'}
            ),
            'factor_ajuste': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ItemPrecioForm(forms.ModelForm):
    class Meta:
        model = ItemPrecio
        fields = ['lista', 'producto', 'precio', 'descuento_maximo']
        widgets = {
            'lista': forms.Select(attrs={'class': 'form-select'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'descuento_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Si es edición, limitar productos a los de la lista
            productos_en_lista = ItemPrecio.objects.filter(
                lista=self.instance.lista
            ).values_list('producto_id', flat=True)
            qs = ProductoTerminado.objects.filter(id__in=productos_en_lista)
        else:
            qs = ProductoTerminado.objects.all()
        self.fields['producto'].queryset = qs
        self.fields['producto'].empty_label = "Seleccione un producto..."
        self.fields['producto'].queryset = ProductoTerminado.objects.all()
        self.fields['producto'].empty_label = "Seleccione producto..."


class PromocionForm(forms.Form):
    """Formulario para marcar productos en oferta con descuento"""
    productos = forms.ModelMultipleChoiceField(
        queryset=InformacionComercial.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Productos a incluir",
        required=True
    )
    descuento_porcentaje = forms.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal('0'), max_value=Decimal('100'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ej: 15.00'}),
        label="Descuento (%)"
    )
    nombre_promocion = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la promoción'}),
        label="Nombre de la Promoción"
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Fecha Inicio"
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Fecha Fin"
    )
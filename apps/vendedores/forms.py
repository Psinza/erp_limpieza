from django import forms
from decimal import Decimal
from .models import Vendedor, Comision

CTR  = {"class": "form-control"}
SEL  = {"class": "form-select"}
NUM  = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}

class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ['usuario', 'codigo_vendedor', 'porcentaje_comision', 'meta_mensual', 'activo']
        widgets = {
            'usuario': forms.Select(attrs=SEL),
            'codigo_vendedor': forms.TextInput(attrs=CTR),
            'porcentaje_comision': forms.NumberInput(attrs=NUM),
            'meta_mensual': forms.NumberInput(attrs=NUM),
            'activo': forms.CheckboxInput(),
        }

class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = ['vendedor', 'fecha', 'monto_venta']
        widgets = {
            'vendedor': forms.Select(attrs=SEL),
            'fecha': forms.DateInput(attrs=DATE),
            'monto_venta': forms.NumberInput(attrs=NUM),
        }

    def clean(self):
        cleaned_data = super().clean()
        monto_venta = cleaned_data.get('monto_venta')
        vendedor = cleaned_data.get('vendedor')

        if monto_venta is not None and vendedor:
            cleaned_data['monto_comision'] = (monto_venta * vendedor.porcentaje_comision) / Decimal('100.00')
        return cleaned_data

from django import forms
from .models import Cliente, Factura, ItemFactura, NotaEntrega, Presupuesto, ItemPresupuesto

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'ruc', 'email', 'telefono', 'direccion', 'activo']

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['numero', 'cliente', 'fecha_emision', 'fecha_vencimiento', 'notas']
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

class ItemFacturaForm(forms.ModelForm):
    class Meta:
        model = ItemFactura
        fields = ['descripcion', 'cantidad', 'precio_unitario']

class NotaEntregaForm(forms.ModelForm):
    class Meta:
        model = NotaEntrega
        fields = ['numero', 'cliente', 'fecha', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['numero', 'cliente', 'fecha_emision', 'fecha_expiracion', 'notas']
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_expiracion': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

class ItemPresupuestoForm(forms.ModelForm):
    class Meta:
        model = ItemPresupuesto
        fields = ['descripcion', 'cantidad', 'precio_unitario']
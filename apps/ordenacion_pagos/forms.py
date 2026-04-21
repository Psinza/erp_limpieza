from django import forms
from .models import SolicitudPago

class SolicitudPagoForm(forms.ModelForm):
    class Meta:
        model = SolicitudPago
        fields = ['descripcion', 'monto', 'fecha_vencimiento', 'notas_auditoria']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'notas_auditoria': forms.Textarea(attrs={'rows': 3}),
        }
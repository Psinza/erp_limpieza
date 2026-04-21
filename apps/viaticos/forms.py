from django import forms
from .models import SolicitudViatico, GastoViatico

class SolicitudViaticoForm(forms.ModelForm):
    class Meta:
        model = SolicitudViatico
        fields = ['destino', 'fecha_inicio', 'fecha_fin', 'motivo', 'monto_solicitado']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

class GastoViaticoForm(forms.ModelForm):
    class Meta:
        model = GastoViatico
        fields = ['tipo', 'descripcion', 'fecha', 'monto', 'comprobante']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
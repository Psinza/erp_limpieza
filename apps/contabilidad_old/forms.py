# apps/contabilidad/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import (
    EjercicioContable, CuentaContable,
    AsientoContable, LineaAsiento,
)

CTR = {"class": "form-control"}
SEL = {"class": "form-select"}
NUM = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}

class EjercicioContableForm(forms.ModelForm):
    class Meta:
        model = EjercicioContable
        fields = ["nombre", "fecha_inicio", "fecha_fin", "abierto"]
        widgets = {
            "nombre": forms.TextInput(attrs=CTR),
            "fecha_inicio": forms.DateInput(attrs=DATE),
            "fecha_fin": forms.DateInput(attrs=DATE),
            "abierto": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class CuentaContableForm(forms.ModelForm):
    class Meta:
        model = CuentaContable
        fields = ["codigo", "nombre", "tipo", "naturaleza", "padre"]
        widgets = {
            "codigo": forms.TextInput(attrs=CTR),
            "nombre": forms.TextInput(attrs=CTR),
            "tipo": forms.Select(attrs=SEL),
            "naturaleza": forms.Select(attrs=SEL),
            "padre": forms.Select(attrs=SEL),
        }

class AsientoContableForm(forms.ModelForm):
    class Meta:
        model = AsientoContable
        fields = ["numero", "ejercicio", "fecha", "glosa", "estado"]
        widgets = { # El campo 'numero' es CharField, no NumberInput
            "numero": forms.TextInput(attrs=CTR), 
            "ejercicio": forms.Select(attrs=SEL),
            "fecha": forms.DateInput(attrs=DATE),
            "glosa": forms.Textarea(attrs=CTR),
            "estado": forms.Select(attrs=SEL),
        }

class LineaAsientoForm(forms.ModelForm):
    class Meta:
        model = LineaAsiento
        fields = ["cuenta", "debe", "haber", "referencia"]
        widgets = {
            "cuenta": forms.Select(attrs=SEL),
            "debe": forms.NumberInput(attrs=NUM),
            "haber": forms.NumberInput(attrs=NUM),
            "referencia": forms.TextInput(attrs=CTR),
        }

# Formset para las líneas de asiento
AsientoContableLineaFormSet = inlineformset_factory(
    AsientoContable,
    LineaAsiento,
    form=LineaAsientoForm,
    extra=2, # Número de formularios vacíos a mostrar inicialmente
    can_delete=True, # Permite eliminar líneas existentes
    fields=["cuenta", "debe", "haber", "referencia"]
)

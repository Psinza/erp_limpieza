# apps/contabilidad/forms.py
from django import forms
from .models import (
    EjercicioContable, CuentaContable,
    AsientoContable, LineaAsiento,
    PeriodoContable, ConfiguracionContable,
)

CTR  = {"class": "form-control"}
SEL  = {"class": "form-select"}
NUM  = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}
CHK  = {"class": "form-check-input"}
TXT  = {"class": "form-control", "rows": 3}


class EjercicioContableForm(forms.ModelForm):
    class Meta:
        model  = EjercicioContable
        fields = ["nombre", "año", "fecha_inicio", "fecha_fin"]
        widgets = {
            "nombre":       forms.TextInput(attrs=CTR),
            "año":          forms.NumberInput(attrs=CTR),
            "fecha_inicio": forms.DateInput(attrs=DATE),
            "fecha_fin":    forms.DateInput(attrs=DATE),
        }


class CuentaContableForm(forms.ModelForm):
    class Meta:
        model  = CuentaContable
        fields = [
            "codigo", "nombre", "tipo", "naturaleza",
            "padre", "nivel", "acepta_movimientos",
            "saldo_inicial", "descripcion", "activa",
        ]
        widgets = {
            "codigo":             forms.TextInput(attrs=CTR),
            "nombre":             forms.TextInput(attrs=CTR),
            "tipo":               forms.Select(attrs=SEL),
            "naturaleza":         forms.Select(attrs=SEL),
            "padre":              forms.Select(attrs=SEL),
            "nivel":              forms.NumberInput(attrs=CTR),
            "acepta_movimientos": forms.CheckboxInput(attrs=CHK),
            "saldo_inicial":      forms.NumberInput(attrs=NUM),
            "descripcion":        forms.Textarea(attrs=TXT),
            "activa":             forms.CheckboxInput(attrs=CHK),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar cuentas de agrupación como padre
        self.fields["padre"].queryset = CuentaContable.objects.filter(
            acepta_movimientos=False, activa=True
        ).order_by("codigo")
        self.fields["padre"].required = False
        self.fields["padre"].empty_label = "— Sin padre (cuenta raíz) —"


class AsientoContableForm(forms.ModelForm):
    class Meta:
        model  = AsientoContable
        fields = ["ejercicio", "fecha", "tipo", "concepto", "referencia"]
        widgets = {
            "ejercicio":  forms.Select(attrs=SEL),
            "fecha":      forms.DateInput(attrs=DATE),
            "tipo":       forms.Select(attrs=SEL),
            "concepto":   forms.TextInput(attrs=CTR),
            "referencia": forms.TextInput(attrs=CTR),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ejercicio"].queryset = EjercicioContable.objects.filter(
            estado="abierto"
        )


class LineaAsientoForm(forms.ModelForm):
    class Meta:
        model  = LineaAsiento
        fields = ["cuenta", "tipo", "monto", "descripcion"]
        widgets = {
            "cuenta":      forms.Select(attrs=SEL),
            "tipo":        forms.Select(attrs=SEL),
            "monto":       forms.NumberInput(attrs=NUM),
            "descripcion": forms.TextInput(attrs=CTR),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cuenta"].queryset = CuentaContable.objects.filter(
            acepta_movimientos=True, activa=True
        ).order_by("codigo")


class PeriodoContableForm(forms.ModelForm):
    class Meta:
        model  = PeriodoContable
        fields = ["ejercicio", "mes", "nombre", "fecha_inicio", "fecha_fin"]
        widgets = {
            "ejercicio":    forms.Select(attrs=SEL),
            "mes":          forms.NumberInput(attrs=CTR),
            "nombre":       forms.TextInput(attrs=CTR),
            "fecha_inicio": forms.DateInput(attrs=DATE),
            "fecha_fin":    forms.DateInput(attrs=DATE),
        }


class ConfiguracionContableForm(forms.ModelForm):
    class Meta:
        model  = ConfiguracionContable
        fields = ["clave", "descripcion", "cuenta"]
        widgets = {
            "clave":       forms.TextInput(attrs=CTR),
            "descripcion": forms.TextInput(attrs=CTR),
            "cuenta":      forms.Select(attrs=SEL),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cuenta"].queryset = CuentaContable.objects.filter(
            activa=True
        ).order_by("codigo")


class FiltroReporteForm(forms.Form):
    """Formulario para filtrar reportes contables."""
    ejercicio = forms.ModelChoiceField(
        queryset=EjercicioContable.objects.all(),
        widget=forms.Select(attrs=SEL),
        required=True,
        label="Ejercicio Contable",
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs=DATE),
        required=False,
        label="Desde",
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs=DATE),
        required=False,
        label="Hasta",
    )

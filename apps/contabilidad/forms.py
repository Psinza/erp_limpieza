from django import forms
from django.forms import inlineformset_factory
from apps.core.models import AsientoContable, LineaAsiento, CuentaContable, EjercicioContable

CTR = {"class": "form-control"}
SEL = {"class": "form-select"}
NUM = {"class": "form-control", "step": "0.01"}
DATE = {"class": "form-control", "type": "date"}

class AsientoContableForm(forms.ModelForm):
    class Meta:
        model = AsientoContable
        fields = ['fecha', 'descripcion', 'ejercicio', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs=DATE),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Concepto del asiento...'}),
            'ejercicio': forms.Select(attrs=SEL),
            'estado': forms.Select(attrs=SEL),
        }

class LineaAsientoForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=[('debe', 'Debe'), ('haber', 'Haber')], widget=forms.Select(attrs=SEL))
    monto = forms.DecimalField(max_digits=15, decimal_places=2, widget=forms.NumberInput(attrs=NUM))

    class Meta:
        model = LineaAsiento
        fields = ['cuenta', 'descripcion']
        widgets = {
            'cuenta': forms.Select(attrs=SEL),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referencia...'}),
        }

LineaAsientoFormSet = inlineformset_factory(
    AsientoContable, LineaAsiento,
    form=LineaAsientoForm,
    extra=5,
    can_delete=True
)

class CuentaContableForm(forms.ModelForm):
    class Meta:
        model = CuentaContable
        fields = ['codigo', 'nombre', 'tipo', 'naturaleza', 'es_cuenta_mayor', 'padre']
        widgets = {
            'codigo': forms.TextInput(attrs=CTR),
            'nombre': forms.TextInput(attrs=CTR),
            'tipo': forms.Select(attrs=SEL),
            'naturaleza': forms.Select(attrs=SEL),
            'es_cuenta_mayor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'padre': forms.Select(attrs=SEL),
        }

class EjercicioContableForm(forms.ModelForm):
    class Meta:
        model = EjercicioContable
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'cerrado']
        widgets = {
            'nombre': forms.TextInput(attrs=CTR),
            'fecha_inicio': forms.DateInput(attrs=DATE),
            'fecha_fin': forms.DateInput(attrs=DATE),
            'cerrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
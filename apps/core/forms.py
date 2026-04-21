from django import forms
from .models import EjercicioContable, CuentaContable, AsientoContable, LineaAsiento, PeriodoContable, ConfiguracionContable

class EjercicioContableForm(forms.ModelForm):
    class Meta:
        model = EjercicioContable
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'cerrado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cerrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CuentaContableForm(forms.ModelForm):
    class Meta:
        model = CuentaContable
        fields = ['codigo', 'nombre', 'tipo', 'naturaleza', 'padre', 'saldo_inicial', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'naturaleza': forms.Select(attrs={'class': 'form-select'}),
            'padre': forms.Select(attrs={'class': 'form-select'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter parent accounts to only show major accounts or accounts that can be parents
        self.fields['padre'].queryset = CuentaContable.objects.filter(es_cuenta_mayor=True, activo=True)
        self.fields['padre'].empty_label = "--- Sin Padre (Cuenta Principal) ---"


class AsientoContableForm(forms.ModelForm):
    class Meta:
        model = AsientoContable
        fields = ['fecha', 'descripcion', 'ejercicio', 'creado_por']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ejercicio': forms.Select(attrs={'class': 'form-select'}),
            'creado_por': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make creado_por optional or set a default if not provided
        self.fields['creado_por'].required = False
        # Filter exercises to only show active ones
        self.fields['ejercicio'].queryset = EjercicioContable.objects.filter(cerrado=False)


class LineaAsientoForm(forms.ModelForm):
    class Meta:
        model = LineaAsiento
        fields = ['cuenta', 'debe', 'haber', 'descripcion']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'debe': forms.NumberInput(attrs={'class': 'form-control'}),
            'haber': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow detail accounts for lines
        self.fields['cuenta'].queryset = CuentaContable.objects.filter(es_cuenta_mayor=False, activo=True)


LineaAsientoFormSet = forms.inlineformset_factory(
    AsientoContable, LineaAsiento,
    form=LineaAsientoForm,
    extra=1,
    can_delete=True
)


class PeriodoContableForm(forms.ModelForm):
    class Meta:
        model = PeriodoContable
        fields = ['ejercicio', 'mes', 'anio', 'fecha_inicio', 'fecha_fin', 'cerrado']
        widgets = {
            'ejercicio': forms.Select(attrs={'class': 'form-select'}),
            'mes': forms.NumberInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cerrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ConfiguracionContableForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionContable
        fields = ['clave', 'cuenta', 'descripcion']
        widgets = {
            'clave': forms.TextInput(attrs={'class': 'form-control'}),
            'cuenta': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow detail accounts for configuration
        self.fields['cuenta'].queryset = CuentaContable.objects.filter(es_cuenta_mayor=False, activo=True)
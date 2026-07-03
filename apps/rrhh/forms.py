# apps/rrhh/forms.py
from django import forms
from .models import Empleado, Departamento, Nomina, Vacacion, Cargo

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nombre', 'departamento', 'nivel', 'sector', 'salario_base_referencial', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'salario_base_referencial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'nacionalidad', 'cedula', 'nombres', 'apellidos', 'departamento', 'cargo', 
            'tipo_contrato', 'salario_base', 'bono_alimentacion', 'bono_divisas',
            'fecha_ingreso', 'cargas_familiares', 'cuenta_bancaria', 'activo',
            'fecha_nacimiento', 'direccion', 'telefono', 'grado_instruccion',
            'tipo_sangre', 'peso', 'estatura', 'enfermedades', 'discapacidad',
            'talla_camisa', 'talla_pantalon', 'talla_calzado'
        ]
        widgets = {
            'nacionalidad': forms.Select(attrs={'class': 'form-select'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'salario_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bono_alimentacion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bono_divisas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cargas_familiares': forms.NumberInput(attrs={'class': 'form-control'}),
            'cuenta_bancaria': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'grado_instruccion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_sangre': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'enfermedades': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'discapacidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'talla_camisa': forms.TextInput(attrs={'class': 'form-control'}),
            'talla_pantalon': forms.TextInput(attrs={'class': 'form-control'}),
            'talla_calzado': forms.TextInput(attrs={'class': 'form-control'}),
        }

class NominaForm(forms.ModelForm):
    class Meta:
        model = Nomina
        fields = ['tipo', 'mes', 'anio', 'tasa_bcv', 'estado']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'mes': forms.Select(attrs={'class': 'form-select'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'tasa_bcv': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class VacacionForm(forms.ModelForm):
    class Meta:
        model = Vacacion
        fields = ['empleado', 'fecha_inicio', 'fecha_fin', 'dias_disfrute', 'bono_vacacional_dias', 'observaciones']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dias_disfrute': forms.NumberInput(attrs={'class': 'form-control'}),
            'bono_vacacional_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

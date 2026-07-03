from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from .models import Empresa, Usuario

class UserRegistrationForm(UserCreationForm):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Rol en la Compañía",
        help_text="Seleccione el departamento o función del usuario.",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ("nombres", "apellidos", "email", "area", "rol") # Añadido rol
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rif': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'J-12345678-0',
                'oninput': 'this.value = this.value.toUpperCase()'
            }),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'contador_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contador_cpc': forms.TextInput(attrs={'class': 'form-control'}),
            'contador_rif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'V-12345678-0',
                'oninput': 'this.value = this.value.toUpperCase()'
            }),
            'gerente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }
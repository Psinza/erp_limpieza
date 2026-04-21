from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Rol, Area, Permiso


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••',
        })
    )


class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 8 caracteres. Dejar en blanco para no cambiar (solo en edición).'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'nombres', 'apellidos',
            'cedula', 'telefono', 'cargo',
            'area', 'rol', 'estado', 'activo', 'foto',
        ]
        widgets = {
            'username':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':     forms.EmailInput(attrs={'class': 'form-control'}),
            'nombres':   forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula':    forms.TextInput(attrs={'class': 'form-control'}),
            'telefono':  forms.TextInput(attrs={'class': 'form-control'}),
            'cargo':     forms.TextInput(attrs={'class': 'form-control'}),
            'area':      forms.Select(attrs={'class': 'form-select'}),
            'rol':       forms.Select(attrs={'class': 'form-select'}),
            'estado':    forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, editar=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.editar = editar
        if editar:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            validate_password(p1)
        elif not self.editar:
            raise forms.ValidationError('La contraseña es obligatoria.')
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            usuario.set_password(p1)
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion', 'nivel', 'areas', 'activo']
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nivel':       forms.Select(attrs={'class': 'form-select'}),
            'areas':       forms.CheckboxSelectMultiple(),
        }


class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ['area', 'accion']
        widgets = {
            'area':   forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'accion': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }


PermisoFormSet = forms.inlineformset_factory(
    Rol, Permiso,
    form=PermisoForm,
    extra=3,
    can_delete=True
)

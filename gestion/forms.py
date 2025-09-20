from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, Rol


class UsuarioCrearForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        required=True,
        label="Rol",
        help_text="Seleccione el rol del usuario",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            rol = self.cleaned_data["rol"]
            PerfilUsuario.objects.update_or_create(usuario=user, defaults={"rol": rol})
        return user


class UsuarioEditarForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña (opcional)", widget=forms.PasswordInput, required=False
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(), required=True, label="Rol"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo",
        }

    def __init__(self, *args, **kwargs):
        self.usuario_obj = kwargs.pop("usuario_obj", None)
        super().__init__(*args, **kwargs)
        # Preseleccionar rol
        if self.instance and self.instance.pk:
            try:
                perfil = PerfilUsuario.objects.get(usuario=self.instance)
                self.fields["rol"].initial = perfil.rol_id
            except PerfilUsuario.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            rol = self.cleaned_data["rol"]
            PerfilUsuario.objects.update_or_create(usuario=user, defaults={"rol": rol})
        return user


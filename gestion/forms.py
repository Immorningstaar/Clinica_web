from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import PerfilUsuario, Rol, Paciente, Profesional


class UsuarioCrearForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(queryset=Rol.objects.none(), required=True, label="Rol")

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
        super().__init__(*args, **kwargs)
        self.fields["rol"].queryset = Rol.objects.all()
        # Todos los campos obligatorios
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields["password"].required = True
        self.fields["rol"].required = True
        # Errores en español
        try:
            self.fields["username"].error_messages.update({
                "required": "El nombre de usuario es obligatorio.",
            })
            self.fields["first_name"].error_messages.update({
                "required": "El nombre es obligatorio.",
            })
            self.fields["last_name"].error_messages.update({
                "required": "El apellido es obligatorio.",
            })
            self.fields["email"].error_messages.update({
                "required": "El correo es obligatorio.",
                "invalid": "El formato del correo no es válido.",
            })
            self.fields["password"].error_messages.update({
                "required": "La contraseña es obligatoria.",
            })
            self.fields["rol"].error_messages.update({
                "required": "Debe seleccionar un rol.",
            })
        except Exception:
            # En caso de caracteres/encoding en el entorno, evitar romper la carga
            pass

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("El correo es obligatorio.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con ese correo.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise forms.ValidationError("La contraseña es obligatoria.")
        # Ejecuta validadores de Django configurados en settings, mapeando mensajes a español
        try:
            validate_password(password)
        except ValidationError as e:
            mensajes = []
            for err in e.error_list:
                code = getattr(err, 'code', '')
                params = getattr(err, 'params', {}) or {}
                if code == 'password_too_short':
                    min_len = params.get('min_length')
                    if min_len:
                        mensajes.append(f"La contraseña debe tener al menos {min_len} caracteres.")
                    else:
                        mensajes.append("La contraseña es demasiado corta.")
                elif code == 'password_too_common':
                    mensajes.append("La contraseña es demasiado común.")
                elif code == 'password_entirely_numeric':
                    mensajes.append("La contraseña no puede ser solo números.")
                elif code == 'password_too_similar':
                    mensajes.append("La contraseña es demasiado similar a tus datos personales.")
                else:
                    mensajes.append("La contraseña no cumple con los requisitos de seguridad.")
            raise forms.ValidationError(mensajes)
        return password

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
        label="Contraseña", widget=forms.PasswordInput, required=True
    )
    rol = forms.ModelChoiceField(queryset=Rol.objects.none(), required=True, label="Rol")

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
        # Preseleccionar rol y cargar queryset
        self.fields["rol"].queryset = Rol.objects.all()
        # Todos los campos obligatorios
        self.fields["username"].required = True
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields["password"].required = True
        self.fields["rol"].required = True
        # Preseleccionar rol
        if self.instance and self.instance.pk:
            try:
                perfil = PerfilUsuario.objects.get(usuario=self.instance)
                self.fields["rol"].initial = perfil.rol_id
            except PerfilUsuario.DoesNotExist:
                pass
        # Errores en español
        try:
            self.fields["username"].error_messages.update({
                "required": "El nombre de usuario es obligatorio.",
            })
            self.fields["email"].error_messages.update({
                "required": "El correo es obligatorio.",
                "invalid": "El formato del correo no es válido.",
            })
            self.fields["password"].error_messages.update({
                "required": "La contraseña es obligatoria.",
            })
            self.fields["rol"].error_messages.update({
                "required": "Debe seleccionar un rol.",
            })
        except Exception:
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

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("El nombre de usuario es obligatorio.")
        qs = User.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("El correo es obligatorio.")
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario registrado con ese correo.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise forms.ValidationError("La contraseña es obligatoria.")
        try:
            validate_password(password, user=self.instance)
        except ValidationError as e:
            mensajes = []
            for err in e.error_list:
                code = getattr(err, 'code', '')
                params = getattr(err, 'params', {}) or {}
                if code == 'password_too_short':
                    min_len = params.get('min_length')
                    if min_len:
                        mensajes.append(f"La contraseña debe tener al menos {min_len} caracteres.")
                    else:
                        mensajes.append("La contraseña es demasiado corta.")
                elif code == 'password_too_common':
                    mensajes.append("La contraseña es demasiado común.")
                elif code == 'password_entirely_numeric':
                    mensajes.append("La contraseña no puede ser solo números.")
                elif code == 'password_too_similar':
                    mensajes.append("La contraseña es demasiado similar a tus datos personales.")
                else:
                    mensajes.append("La contraseña no cumple con los requisitos de seguridad.")
            raise forms.ValidationError(mensajes)
        return password

# Formulario para editar el perfil del PACIENTE
class PacientePerfilForm(forms.ModelForm):
    # La fecha de nacimiento SOLO va aquí
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = Paciente
        # Campos editables del Paciente (asumo que tiene 'direccion' y 'celular' como en el registro)
        fields = ('direccion', 'celular', 'fecha_nacimiento') 
        labels = {
            'celular': 'Teléfono',
        }
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
        }

# 2. Formulario para editar el perfil del PROFESIONAL
class ProfesionalPerfilForm(forms.ModelForm):
    # El profesional no edita su especialidad, ni fecha de nacimiento, solo lo de contacto
    
    class Meta:
        model = Profesional
        # Campos editables del Profesional (Dirección y Teléfono)
        fields = ('direccion', 'celular') 
        labels = {
            'celular': 'Teléfono',
        }
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
        }
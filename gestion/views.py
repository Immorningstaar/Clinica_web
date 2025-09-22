
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction 
import re 
from .models import Paciente, Profesional, Rol, PerfilUsuario 

# Función auxiliar para validar las 4 reglas de la contraseña
def validar_contraseña(password):
    errores_contraseña = []
    
    # Regla 1: Al menos 8 caracteres
    if len(password) < 8:
        errores_contraseña.append("La contraseña debe tener al menos 8 caracteres.")
    # Regla 2: Al menos una mayúscula
    if not re.search(r'[A-Z]', password):
        errores_contraseña.append("La contraseña debe contener al menos una letra mayúscula.")
    # Regla 3: Al menos un número
    if not re.search(r'[0-9]', password):
        errores_contraseña.append("La contraseña debe contener al menos un número.")
    # Regla 4: Al menos un carácter especial (@$!%*?&)
    if not re.search(r'[\@$!%*?&]', password):
        errores_contraseña.append("La contraseña debe contener al menos un carácter especial (@$!%*?&).")

    return errores_contraseña


@transaction.atomic 
def registro(request):
    if request.method == 'POST':
        # --- 1. Obtener datos del formulario POST ---
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email') # ¡Cuidado! En tu HTML es 'email' (name del input)
        rut = request.POST.get('rut')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        # Utilizamos 'rol' porque ese es el name del select en tu último HTML.
        tipo_usuario = request.POST.get('rol') 
        
        errores = []
        
        # --- 2. Validación de Datos ---
        if password != confirm_password:
            errores.append("Las contraseñas no coinciden.")
            
        errores.extend(validar_contraseña(password))
        
        # Validaciones de unicidad (Email)
        if User.objects.filter(email=email).exists():
            errores.append("Ya existe un usuario con este correo electrónico.")
            
        # Validaciones de unicidad (RUT, chequeando ambos modelos)
        if Paciente.objects.filter(rut=rut).exists() or Profesional.objects.filter(rut=rut).exists():
             errores.append("Ya existe un usuario (paciente o profesional) con este RUT.")
        
        # Validación de selección de rol
        if tipo_usuario not in ['paciente', 'profesional']:
             errores.append("Debe seleccionar un tipo de cuenta válido (Paciente o Profesional).")

        if errores:
            # Renderizar con errores y los datos para que el usuario no pierda lo que escribió
            return render(request, 'registro.html', {'errores': errores, 'datos': request.POST}) 

        # --- 3. Crear Usuario y Perfil si la validación es exitosa ---
        try:
            # Crear el objeto User base (Django hashea la contraseña)
            user = User.objects.create_user(
                username=email, # Usamos el email como username
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellidos
            )
            
            # Crear el perfil específico (Paciente o Profesional)
            if tipo_usuario == 'paciente':
                Paciente.objects.create(
                    usuario=user,
                    rut=rut,
                    direccion=direccion,
                    celular=telefono
                )
                rol_nombre = 'Paciente'
                
            elif tipo_usuario == 'profesional':
                # Creamos el Profesional, omitiendo la especialidad.
                # ASUMIMOS que el campo especialidad en models.py tiene null=True, blank=True
                Profesional.objects.create(
                    usuario=user,
                    rut=rut,
                    # Dejamos especialidad vacío o con un valor por defecto si es necesario
                    # Si el campo es CharField, se guarda como cadena vacía ('')
                )
                rol_nombre = 'Profesional'
            
            # Asignar el Rol a través del modelo PerfilUsuario
            rol = Rol.objects.get(nombre__iexact=rol_nombre)
            PerfilUsuario.objects.create(usuario=user, rol=rol)

            # Redirigir al login después de un registro exitoso
            return redirect('login') 
            
    
        except IntegrityError:
            # Esto podría ocurrir si hay un problema de unicidad no detectado antes.
            errores.append("Hubo un error al crear el usuario. Inténtelo de nuevo.")
            return render(request, 'registro.html', {'errores': errores}) 

    # Manejar la petición GET (mostrar el formulario vacío)
    return render(request, 'registro.html')

# Create your views here.
def index(request):
    return render(request, 'index.html')

def profesionales(request):
    return render(request, 'profesionales.html')

def pagos(request):
    return render(request, 'pagos.html')    

def centro(request):
    return render(request, 'centro.html')

def admision(request):
    return render(request, 'admision.html') 

def galerias(request):
    return render(request, 'galerias.html') 

def login(request):
    return render(request, 'login.html')    

def perfil(request):
    return render(request, 'perfil.html')

def recuperar(request):
    return render(request, 'recuperar.html')



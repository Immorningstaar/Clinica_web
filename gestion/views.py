from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models import ObjectDoesNotExist
import re 
import random
from datetime import timedelta
from django.urls import reverse 
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profesional
from .serializers import ProfesionalSerializer


# Modelos y Formularios
from .models import Paciente, Profesional, Rol, PerfilUsuario, PasswordResetCode
from .forms import UsuarioCrearForm, UsuarioEditarForm, PacientePerfilForm, ProfesionalPerfilForm
from .decorators import admin_required


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
        fecha_nacimiento = request.POST.get('fecha_nacimiento') 
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
                    celular=telefono,
                    fecha_nacimiento=fecha_nacimiento
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

def index(request):
    return render(request, 'index.html')





# --- Administración de usuarios (CRUD para Administrador) ---
def _usuario_es_admin(user) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    try:
        perfil = PerfilUsuario.objects.select_related("rol").get(usuario=user)
        return perfil.rol.nombre.lower() == "administrador"
    except PerfilUsuario.DoesNotExist:
        return False


@admin_required
def gestion_usuarios(request):

    # Asegurar que exista el rol Administrador para el formulario
    Rol.objects.get_or_create(nombre="Administrador")

    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente")
            return redirect("gestion_usuarios")
        else:
            messages.error(request, "Revisa los datos del formulario")
    else:
        form = UsuarioCrearForm()

    consulta = request.GET.get("q", "").strip()
    usuarios = User.objects.all().order_by("username")
    if consulta:
        usuarios = (
            usuarios.filter(username__icontains=consulta)
            | usuarios.filter(first_name__icontains=consulta)
            | usuarios.filter(last_name__icontains=consulta)
        )

    usuarios_info = []
    for u in usuarios:
        try:
            rol_nombre = u.perfilusuario.rol.nombre
        except PerfilUsuario.DoesNotExist:
            rol_nombre = "Sin perfil"
        usuarios_info.append({"obj": u, "rol": rol_nombre})

    contexto = {
        "usuarios": usuarios_info,
        "form": form,
        "modo": "crear",
    }
    return render(request, "admin/gestion_usuarios.html", contexto)


@admin_required
def editar_usuario(request, user_id: int):

    usuario = get_object_or_404(User, pk=user_id)
    Rol.objects.get_or_create(nombre="Administrador")

    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect("gestion_usuarios")
        else:
            messages.error(request, "No se pudo actualizar. Verifica los campos")
    else:
        form = UsuarioEditarForm(instance=usuario)

    usuarios = User.objects.all().order_by("username")
    usuarios_info = []
    for u in usuarios:
        try:
            rol_nombre = u.perfilusuario.rol.nombre
        except PerfilUsuario.DoesNotExist:
            rol_nombre = "Sin perfil"
        usuarios_info.append({"obj": u, "rol": rol_nombre})

    contexto = {
        "usuarios": usuarios_info,
        "form": form,
        "modo": "editar",
        "usuario_editar": usuario,
    }
    return render(request, "admin/gestion_usuarios.html", contexto)


@admin_required
def eliminar_usuario(request, user_id: int):
    usuario = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente")
        return redirect("gestion_usuarios")
    # Confirmación simple en la misma pantalla usando GET -> POST automático
    usuarios = User.objects.all().order_by("username")
    usuarios_info = []
    for u in usuarios:
        try:
            rol_nombre = u.perfilusuario.rol.nombre
        except PerfilUsuario.DoesNotExist:
            rol_nombre = "Sin perfil"
        usuarios_info.append({"obj": u, "rol": rol_nombre})

    return render(
        request,
        "admin/gestion_usuarios.html",
        {
            "usuarios": usuarios_info,
            "confirmar_eliminacion": usuario,
            "form": UsuarioCrearForm(),
            "modo": "crear",
        },
    )


# --- Recuperación de contraseña (FP-03) ---
def recuperar(request):
    # Pantalla donde el usuario pide el código y cambia su clave.
    # El JS llama a los endpoints de abajo.
    return render(request, 'recuperar.html')


@require_POST
def solicitar_codigo_recuperacion(request):
    # Genera y guarda el código (respuesta genérica para no filtrar correos)
    correo = request.POST.get("email", "").strip().lower()
    if not correo:
        return JsonResponse({"ok": False, "error": "Correo requerido"}, status=400)

    try:
        user = User.objects.get(email__iexact=correo)
    except User.DoesNotExist:
        return JsonResponse({"ok": True, "mensaje": "Si el correo existe, enviaremos un código."})

    codigo = f"{random.randint(0, 999999):06d}"
    ahora = timezone.now()
    expira = ahora + timedelta(minutes=10)
    PasswordResetCode.objects.create(usuario=user, codigo=codigo, expira_en=expira)

    data = {"ok": True, "ttl": 600}
    if settings.DEBUG:
        # En desarrollo exponemos el código para facilitar pruebas
        data["codigo_debug"] = codigo
    return JsonResponse(data)


@require_POST
@transaction.atomic
def reset_password_con_codigo(request):
    # Valida código vigente y cambia la clave con set_password
    correo = request.POST.get("email", "").strip().lower()
    codigo = request.POST.get("codigo", "").strip()
    nueva = request.POST.get("password", "")

    if not (correo and codigo and nueva):
        return JsonResponse({"ok": False, "error": "Datos incompletos"}, status=400)

    try:
        user = User.objects.get(email__iexact=correo)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Código inválido o expirado"}, status=400)

    ahora = timezone.now()
    # Evitar select_for_update + LIMIT (Oracle no lo soporta)
    qs = (
        PasswordResetCode.objects
        .filter(usuario=user, codigo=codigo, utilizado=False, expira_en__gte=ahora)
        .order_by('-creado_en')
    )
    obj = qs.first()
    if not obj:
        return JsonResponse({"ok": False, "error": "Código inválido o expirado"}, status=400)

    user.set_password(nueva)
    user.save(update_fields=["password"])
    updated = PasswordResetCode.objects.filter(pk=obj.pk, utilizado=False).update(utilizado=True, usado_en=ahora)
    if updated == 0:
        return JsonResponse({"ok": False, "error": "El código ya fue utilizado"}, status=400)

    return JsonResponse({"ok": True})


# SEG-01: Vistas de autenticación y páginas protegidas
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            
            redirect_url = reverse('perfil')
            
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        else:
            return JsonResponse({'success': False, 'message': 'Credenciales inválidas. Verifica tu correo y contraseña.'}, status=401)

    return render(request, 'login.html')


# Vistas de autenticación y páginas protegidas
@login_required
def perfil_page(request):
    
    # 1. Determinar el Rol y el Objeto de Perfil Específico
    rol = 'N/A'
    perfil_obj = None 
    perfil_form = None
    
    try:
        # A) Obtener el nombre del Rol y la Clase de Formulario correcta
        rol = request.user.perfilusuario.rol.nombre
        
        if rol.lower() == 'paciente':
            perfil_obj = request.user.paciente
            PerfilFormClass = PacientePerfilForm
        elif rol.lower() == 'profesional':
            perfil_obj = request.user.profesional
            PerfilFormClass = ProfesionalPerfilForm
        else:
            # Manejar el caso de Administrador u otro rol sin perfil editable
            messages.info(request, "Tu rol no tiene un perfil específico editable.")
            context = { 'perfil_form': None, 'rol_fijo': rol, 'rut_fijo': 'N/A' }
            return render(request, 'perfil.html', context)
        
    except ObjectDoesNotExist:
        messages.error(request, "Error de perfil: Tu cuenta no tiene un perfil asociado (Paciente o Profesional).")
        context = { 'perfil_form': None, 'rol_fijo': rol, 'rut_fijo': 'N/A' }
        return render(request, 'perfil.html', context)
    
    
    # 2. Manejo de POST (Guardar Perfil y/o Cambiar Contraseña)
    if request.method == 'POST':
        
        # --- A. Edición de Perfil (Dirección, Teléfono, Fecha Nac.) ---
        perfil_form = PerfilFormClass(request.POST, instance=perfil_obj)

        if perfil_form.is_valid():
            perfil_form.save()
            messages.success(request, '¡Información de contacto actualizada con éxito!')
        else:
            messages.error(request, 'Error al actualizar el perfil. Revisa la Dirección y Teléfono.')


        # --- B. Cambio de Contraseña (Utilizando tu función validar_contraseña) ---
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')
        
        # Solo procesamos si hay intento de cambio
        if current_password or new_password or confirm_password: 
            
            if not request.user.check_password(current_password):
                messages.error(request, 'La Contraseña Actual no es correcta.')
            elif not new_password:
                messages.error(request, 'La Nueva Contraseña no puede estar vacía.')
            elif new_password != confirm_password:
                messages.error(request, 'La Nueva Contraseña y la Confirmación no coinciden.')
            else:
                # La función validar_contraseña está definida y lista para usarse
                errores_contraseña = validar_contraseña(new_password) 
                
                if errores_contraseña:
                    for error in errores_contraseña:
                        messages.error(request, f'Contraseña: {error}') 
                else:
                    # ¡GUARDAR LA NUEVA CONTRASEÑA!
                    request.user.set_password(new_password)
                    request.user.save()
                    
                    # ESENCIAL: Mantenemos la sesión activa
                    update_session_auth_hash(request, request.user)
                    
                    messages.success(request, '¡Contraseña cambiada con éxito!')
        
        # Redirigir para evitar re-envío del formulario al refrescar
        return redirect('perfil') 

    # 3. Manejo de GET (Mostrar el formulario por primera vez)
    # Si la vista no entró en POST, creamos el formulario inicial
    perfil_form = PerfilFormClass(instance=perfil_obj)

    # --- 4. Preparar el Contexto Final ---
    context = {
        'perfil_form': perfil_form, 
        # RUT: El RUT está en el objeto específico (Paciente/Profesional)
        'rut_fijo': perfil_obj.rut, 
        'rol_fijo': rol, 
    }
    
    return render(request, 'perfil.html', context)

# Vistas de navegación que no necesitan protección
def index(request):
    # Se pasa el objeto request.user al contexto, ya sea un usuario logueado o anónimo.
    context = {
        'user': request.user
    }
    return render(request, 'index.html', context)


def profesionales(request):
    return render(request, 'profesionales.html')

def pago(request):
    return render(request, 'pago.html') 

def centro(request):
    return render(request, 'centro.html')

def admision(request):
    return render(request, 'admision.html') 

def galerias(request):
    return render(request, 'galerias.html') 

def logout_page(request):
    logout(request)
    # Redirigir al usuario al index después de cerrar sesión
    return redirect('index')

# API Profesionales
class ProfesionalListAPIView(APIView):
    def get(self, request):
        profesionales = Profesional.objects.all()
        serializer = ProfesionalSerializer(profesionales, many=True)
        return Response(serializer.data)

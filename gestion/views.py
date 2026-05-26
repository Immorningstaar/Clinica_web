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
from decimal import Decimal
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profesional
from .serializers import ProfesionalSerializer
import requests


# Modelos y Formularios
from .models import Paciente, Profesional, Rol, PerfilUsuario, PasswordResetCode, Cita, Atencion, Diagnostico, Pago, Presupuesto
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
        email = request.POST.get('email') # (name del input)
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
                especialidad = request.POST.get('especialidad', '').strip()
                if not especialidad:
                    errores.append("La especialidad es obligatoria para profesionales.")
                    user.delete()
                    return render(request, 'registro.html', {'errores': errores, 'datos': request.POST})
                Profesional.objects.create(
                    usuario=user,
                    rut=rut,
                    especialidad=especialidad,
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
    datos_clima = None
    
    try:
        api_key = settings.WEATHERSTACK_API_KEY
    except AttributeError:
        print("Error: WEATHERSTACK_API_KEY no está definida en settings.py.")
        context = { 'user': request.user, 'datos_clima': None }
        return render(request, 'index.html', context)
    
    WEATHERSTACK_URL = f'http://api.weatherstack.com/current?access_key={api_key}&query=Santiago&units=m'
    
    try:
        response_clima = requests.get(WEATHERSTACK_URL, timeout=5)
        response_clima.raise_for_status()
        
        data_clima = response_clima.json()
        
        if data_clima.get('success', True) == False:
             error_info = data_clima.get('error', {}).get('info', 'Error desconocido de Weatherstack.')
             raise Exception(f"Error de la API de Weatherstack: {error_info}")


        current = data_clima.get('current', {})
        location = data_clima.get('location', {})
        
        datos_clima = {
            'ciudad': location.get('name', 'N/A'),
            'temperatura': f"{current.get('temperature', 'N/A')}°C",
            'sensacion_termica': f"{current.get('feelslike', 'N/A')}°C",
            'descripcion': current.get('weather_descriptions', ['Sin datos'])[0],
            'humedad': f"{current.get('humidity', 'N/A')}%",
            'viento': f"{current.get('wind_speed', 'N/A')} km/h",
        }

    except requests.exceptions.RequestException as e:
        print(f"Advertencia: Error de conexión HTTP o Timeout. {e}")
        datos_clima = None
    except Exception as e:
        print(f"Advertencia: Error al procesar datos de clima. {e}")
        datos_clima = None


    context = {
        'user': request.user,
        'datos_clima': datos_clima, 
    }
    
    return render(request, 'index.html', context)


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
        perfil_form = PerfilFormClass(request.POST, request.FILES, instance=perfil_obj)

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

def profesionales(request):
    profesionales = Profesional.objects.select_related('usuario').all()
    return render(request, 'profesionales.html', {'profesionales': profesionales})

def pago(request):
    valor_uf = None

    try:
        response = requests.get('https://mindicador.cl/api/uf')
        response.raise_for_status()
        data = response.json()
        valor_uf = data['serie'][0]['valor']
    
    except requests.exceptions.RequestException as e:
        print(f"Error al consumir UF API: {e}")
        valor_uf = "No disponible."

    citas_pendientes = []
    if request.user.is_authenticated:
        try:
            paciente = request.user.paciente
            qs = Cita.objects.filter(
                paciente=paciente,
                tipo="consulta",
                estado="Agendada"
            ).select_related('profesional__usuario').order_by('fecha_hora')
            for c in qs:
                base = Decimal("30000")
                iva = base * Decimal("0.19")
                c.monto_base = base
                c.monto_iva = iva
                c.monto_total = base + iva
            citas_pendientes = qs
        except Paciente.DoesNotExist:
            pass
    
    context = {
        'valor_uf': valor_uf,
        'citas_pendientes': citas_pendientes,
    }

    return render(request, 'pago.html', context) 

def centro(request):
    return render(request, 'centro.html')

def admision(request):
    context = {}
    if request.user.is_authenticated:
        try:
            p = request.user.paciente
            context['datos_paciente'] = {
                'nombre': request.user.first_name,
                'apellidos': request.user.last_name,
                'rut': p.rut,
                'fecha_nacimiento': p.fecha_nacimiento.isoformat(),
                'telefono': p.celular,
                'correo': request.user.email,
                'direccion': p.direccion,
            }
        except Paciente.DoesNotExist:
            pass
    profesionales = Profesional.objects.select_related('usuario').all()
    context['profesionales'] = profesionales
    return render(request, 'admision.html', context) 

def galerias(request):
    return render(request, 'galerias.html') 

def logout_page(request):
    logout(request)
    # Redirigir al usuario al index después de cerrar sesión
    return redirect('index')

# --- Reserva de Citas ---
BLOQUES_HORARIOS = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30) if not (h == 18 and m == 30)]

@login_required
def horas_ocupadas(request):
    profesional_id = request.GET.get('profesional_id')
    fecha = request.GET.get('fecha')
    if not profesional_id or not fecha:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    citas = Cita.objects.filter(
        profesional_id=profesional_id,
        fecha_hora__date=fecha,
        estado__in=("Agendada", "En curso", "Confirmada"),
    ).values_list('fecha_hora__time', flat=True)
    ocupadas = [c.strftime('%H:%M') for c in citas]
    return JsonResponse({'ocupadas': ocupadas})


@login_required
def reservar_cita(request):
    if request.method == 'POST':
        profesional_id = request.POST.get('profesional')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        motivo = request.POST.get('motivo')

        errores = []
        if not profesional_id:
            errores.append("Debe seleccionar un profesional.")
        if not fecha:
            errores.append("Debe seleccionar una fecha.")
        if not hora:
            errores.append("Debe seleccionar un horario.")
        if not motivo:
            errores.append("El motivo es obligatorio.")

        if errores:
            profesionales = Profesional.objects.select_related('usuario').all()
            return render(request, 'reservar.html', {'errores': errores, 'profesionales': profesionales, 'datos': request.POST, 'bloques_horarios': BLOQUES_HORARIOS})

        try:
            fecha_hora = timezone.datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            if timezone.is_naive(fecha_hora):
                fecha_hora = timezone.make_aware(fecha_hora)

            ahora = timezone.localtime()
            if fecha_hora.date() < ahora.date():
                errores.append(f"La fecha {fecha} es anterior a hoy. No se puede agendar una cita en el pasado.")
            if fecha_hora.date() == ahora.date() and fecha_hora.time() <= ahora.time():
                errores.append(f"La hora {hora} de hoy ya pasó. Seleccione un horario posterior a las {ahora.strftime('%H:%M')}.")

            if errores:
                profesionales = Profesional.objects.select_related('usuario').all()
                return render(request, 'reservar.html', {'errores': errores, 'profesionales': profesionales, 'datos': request.POST, 'bloques_horarios': BLOQUES_HORARIOS})

            paciente = request.user.paciente
            profesional = Profesional.objects.get(pk=profesional_id)

            if Cita.objects.filter(
                profesional=profesional,
                fecha_hora=fecha_hora,
                estado__in=("Agendada", "En curso", "Confirmada"),
            ).exists():
                errores.append(f"El horario {hora} del {fecha} ya está reservado para Dr(a). {profesional.usuario.first_name} {profesional.usuario.last_name}. Seleccione otro horario.")
                profesionales = Profesional.objects.select_related('usuario').all()
                return render(request, 'reservar.html', {'errores': errores, 'profesionales': profesionales, 'datos': request.POST, 'bloques_horarios': BLOQUES_HORARIOS})

            cita = Cita.objects.create(
                paciente=paciente,
                profesional=profesional,
                fecha_hora=fecha_hora,
                motivo=motivo,
                tipo="consulta",
                estado="Agendada"
            )
            messages.success(request, f"Cita #{cita.id} agendada correctamente con Dr(a). {profesional.usuario.first_name} {profesional.usuario.last_name}.")
            return redirect('perfil')
        except IntegrityError:
            errores.append(f"El horario {hora} del {fecha} ya está reservado para Dr(a). {profesional.usuario.first_name} {profesional.usuario.last_name}. Seleccione otro horario.")
            profesionales = Profesional.objects.select_related('usuario').all()
            return render(request, 'reservar.html', {'errores': errores, 'profesionales': profesionales, 'datos': request.POST, 'bloques_horarios': BLOQUES_HORARIOS})
        except Paciente.DoesNotExist:
            errores.append("Debe estar registrado como paciente para agendar una cita.")
            profesionales = Profesional.objects.select_related('usuario').all()
            return render(request, 'reservar.html', {'errores': errores, 'profesionales': profesionales, 'datos': request.POST, 'bloques_horarios': BLOQUES_HORARIOS})
        except Profesional.DoesNotExist:
            errores.append("El profesional seleccionado no existe.")
            profesionales = Profesional.objects.select_related('usuario').all()
            return render(request, 'reservar.html', {'errores': errores, 'profesionales': profesionales, 'datos': request.POST, 'bloques_horarios': BLOQUES_HORARIOS})

    profesionales = Profesional.objects.select_related('usuario').all()
    ahora = timezone.localtime()
    return render(request, 'reservar.html', {
        'profesionales': profesionales,
        'bloques_horarios': BLOQUES_HORARIOS,
        'hoy_iso': ahora.strftime('%Y-%m-%d'),
        'hora_actual': ahora.strftime('%H:%M'),
    })


# --- Pago ---
@login_required
@require_POST
def procesar_pago(request):
    cita_id = request.POST.get('cita_id')
    monto = request.POST.get('monto')
    metodo = request.POST.get('metodo', 'WebPay')

    if not all([cita_id, monto]):
        return JsonResponse({'ok': False, 'error': 'Datos incompletos'}, status=400)

    try:
        cita = Cita.objects.get(pk=cita_id, paciente=request.user.paciente)
    except (Cita.DoesNotExist, Paciente.DoesNotExist):
        return JsonResponse({'ok': False, 'error': 'Cita no encontrada'}, status=404)

    if cita.estado == "Pagado":
        return JsonResponse({'ok': False, 'error': 'Esta cita ya fue pagada.'}, status=400)

    Pago.objects.create(
        cita=cita,
        monto=monto,
        metodo=metodo,
    )
    cita.estado = "Pagado"
    cita.save(update_fields=["estado"])

    webpay_id = f"WEBPAY-{cita.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    return JsonResponse({
        'ok': True,
        'mensaje': 'Pago registrado exitosamente',
        'webpay_id': webpay_id,
    })


# --- WebPay Simulación ---
@login_required
def webpay_simular(request, cita_id):
    try:
        cita = Cita.objects.get(pk=cita_id, paciente=request.user.paciente)
    except (Cita.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, "Cita no encontrada.")
        return redirect('pago')

    if cita.estado != "Agendada":
        messages.error(request, "Esta cita no está pendiente de pago.")
        return redirect('pago')

    base = Decimal("30000")
    iva = base * Decimal("0.19")
    total = base + iva

    if request.method == 'POST':
        Pago.objects.create(cita=cita, monto=total, metodo="WebPay")
        cita.estado = "Pagado"
        cita.save(update_fields=["estado"])
        webpay_id = f"WEBPAY-{cita.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        messages.success(request, f"Pago exitoso. Transacción {webpay_id}. Se ha enviado tu boleta al correo registrado.")
        return redirect('pago')

    return render(request, 'webpay_simulacion.html', {
        'cita': cita,
        'monto_base': base,
        'monto_iva': iva,
        'monto_total': total,
    })


# --- Admisión / Presupuesto ---
@login_required
def solicitar_presupuesto(request):
    if request.method == 'POST':
        try:
            paciente = request.user.paciente
        except Paciente.DoesNotExist:
            messages.error(request, "Debe estar registrado como paciente para solicitar un presupuesto.")
            return redirect('admision')

        nombre = request.POST.get('nombre', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        rut = request.POST.get('rut', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '')
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        comuna = request.POST.get('comuna', '').strip()
        medico_tratante = request.POST.get('medico_tratante', '').strip()
        prevision = request.POST.get('prevision', '').strip()

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not apellidos:
            errores.append("Los apellidos son obligatorios.")
        if not rut:
            errores.append("El RUT es obligatorio.")
        if not fecha_nacimiento:
            errores.append("La fecha de nacimiento es obligatoria.")
        if not telefono:
            errores.append("El teléfono es obligatorio.")
        if not correo:
            errores.append("El correo es obligatorio.")

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('admision')

        presupuesto = Presupuesto.objects.create(
            paciente=paciente,
            rut=rut,
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            correo=correo,
            comuna=comuna,
            medico_tratante=medico_tratante,
            prevision=prevision,
            documento=request.FILES.get('documento'),
        )

        messages.success(
            request,
            f"Solicitud de presupuesto #{presupuesto.id} enviada correctamente. "
            f"Monto estimado: ${presupuesto.monto_estimado:,.0f} CLP. "
            "Nos pondremos en contacto contigo para confirmar."
        )
        return redirect('perfil')

    return redirect('admision')


# --- Atenciones y Diagnósticos ---
@login_required
def registrar_atencion(request, cita_id):
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, "Solo los profesionales pueden registrar atenciones.")
        return redirect('perfil')

    cita = get_object_or_404(Cita, pk=cita_id, profesional=profesional)

    if cita.estado not in ("Agendada", "En curso"):
        messages.error(request, "Esta cita no puede ser atendida.")
        return redirect('agenda_medico')

    if request.method == 'POST':
        notas = request.POST.get('notas', '').strip()
        codigo_diag = request.POST.get('codigo_diagnostico', '').strip()
        descripcion_diag = request.POST.get('descripcion_diagnostico', '').strip()
        indicaciones = request.POST.get('indicaciones', '').strip()

        if not notas:
            messages.error(request, "Las notas de evolución son obligatorias.")
            return render(request, 'atencion.html', {'cita': cita})

        atencion = Atencion.objects.create(cita=cita, notas=notas, indicaciones=indicaciones)

        if codigo_diag and descripcion_diag:
            Diagnostico.objects.create(
                atencion=atencion,
                codigo=codigo_diag,
                descripcion=descripcion_diag,
            )

        cita.estado = "Atendida"
        cita.save(update_fields=["estado"])

        messages.success(request, "Consulta finalizada y registrada correctamente.")
        return redirect('agenda_medico')

    # GET: marcar como "En curso" al abrir la ficha
    if cita.estado == "Agendada":
        cita.estado = "En curso"
        cita.save(update_fields=["estado"])

    return render(request, 'atencion.html', {'cita': cita})


# --- Historial Clínico ---
@login_required
def historial_paciente(request):
    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        messages.error(request, "Solo los pacientes pueden ver su historial.")
        return redirect('perfil')

    citas = Cita.objects.filter(paciente=paciente).select_related('profesional__usuario').order_by('-fecha_hora')

    historial = []
    for cita in citas:
        atencion = getattr(cita, 'atencion', None)
        diagnosticos = Diagnostico.objects.filter(atencion=atencion) if atencion else []
        pago = getattr(cita, 'pago', None)
        historial.append({
            'cita': cita,
            'atencion': atencion,
            'diagnosticos': diagnosticos,
            'pago': pago,
        })

    return render(request, 'historial.html', {'historial': historial})


# --- Cancelar Cita ---
@login_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)

    es_paciente = False
    es_profesional = False
    try:
        es_paciente = cita.paciente == request.user.paciente
    except Paciente.DoesNotExist:
        pass
    try:
        es_profesional = cita.profesional == request.user.profesional
    except Profesional.DoesNotExist:
        pass

    if not es_paciente and not es_profesional:
        messages.error(request, "No tienes permiso para cancelar esta cita.")
        return redirect('perfil')

    if cita.estado not in ("Agendada", "En curso"):
        messages.error(request, "Solo se pueden cancelar citas agendadas o en curso.")
        return redirect('perfil')

    cita.estado = "Cancelada"
    cita.save(update_fields=["estado"])
    messages.success(request, f"Cita #{cita.id} cancelada correctamente.")

    referer = request.META.get('HTTP_REFERER', '')
    if 'agenda' in referer:
        return redirect('agenda_medico')
    return redirect('mis_citas')


# --- Mis Citas (Paciente) ---
@login_required
def mis_citas(request):
    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        messages.error(request, "Solo los pacientes pueden ver sus citas.")
        return redirect('perfil')

    citas = Cita.objects.filter(paciente=paciente).select_related('profesional__usuario').order_by('-fecha_hora')
    return render(request, 'mis_citas.html', {'citas': citas})


# --- Agenda Médico ---
@login_required
def agenda_medico(request):
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, "Solo los profesionales pueden acceder a la agenda.")
        return redirect('perfil')

    hoy = timezone.localdate()
    citas = Cita.objects.filter(
        profesional=profesional,
        fecha_hora__date=hoy,
    ).select_related('paciente__usuario').order_by('fecha_hora')

    return render(request, 'agenda.html', {
        'profesional': profesional,
        'citas': citas,
        'hoy': hoy,
    })


# API Profesionales
class ProfesionalListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profesionales = Profesional.objects.all()
        serializer = ProfesionalSerializer(profesionales, many=True)
        return Response(serializer.data)

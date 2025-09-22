from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
import random
from datetime import timedelta

from .models import PerfilUsuario, Rol, PasswordResetCode
from .forms import UsuarioCrearForm, UsuarioEditarForm
from .decorators import admin_required


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
            return redirect("gestion_usuarios")
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
            return redirect("gestion_usuarios")
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
    # Página de inicio de sesión (solo renderiza el template)
    return render(request, 'login.html')


@login_required
def perfil(request):
    # Página de perfil del usuario, requiere autenticación
    return render(request, 'perfil.html')

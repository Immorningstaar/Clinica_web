from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import PerfilUsuario, Rol
from .forms import UsuarioCrearForm, UsuarioEditarForm


def index(request):
    return render(request, 'index.html')


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


def gestion_usuarios(request):
    if not request.user.is_authenticated or not _usuario_es_admin(request.user):
        return HttpResponseForbidden("Acceso restringido a administradores")

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
        usuarios = usuarios.filter(
            username__icontains=consulta
        ) | usuarios.filter(first_name__icontains=consulta) | usuarios.filter(
            last_name__icontains=consulta
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


def editar_usuario(request, user_id: int):
    if not request.user.is_authenticated or not _usuario_es_admin(request.user):
        return HttpResponseForbidden("Acceso restringido a administradores")

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


def eliminar_usuario(request, user_id: int):
    if not request.user.is_authenticated or not _usuario_es_admin(request.user):
        return HttpResponseForbidden("Acceso restringido a administradores")
    usuario = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        usuario.delete()
        return redirect("gestion_usuarios")
    # Para confirmación simple en la misma pantalla usando GET -> POST automático
    usuarios = User.objects.all().order_by("username")
    usuarios_info = []
    for u in usuarios:
        try:
            rol_nombre = u.perfilusuario.rol.nombre
        except PerfilUsuario.DoesNotExist:
            rol_nombre = "Sin perfil"
        usuarios_info.append({"obj": u, "rol": rol_nombre})

    return render(request, "admin/gestion_usuarios.html", {
        "usuarios": usuarios_info,
        "confirmar_eliminacion": usuario,
        "form": UsuarioCrearForm(),
        "modo": "crear",
    })

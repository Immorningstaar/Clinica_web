from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from .models import PerfilUsuario


def role_required(*role_names, allow_superuser=True, redirect_unauthorized=None):
    """
    Requiere que el usuario esté autenticado y tenga alguno de los roles dados.

    - role_names: nombres de roles aceptados (p.ej. "Administrador").
    - allow_superuser: si True, un superusuario pasa la verificación.
    - redirect_unauthorized: URL a la que redirigir si el usuario autenticado
      no tiene el rol. Si es None, devuelve 403 Forbidden.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                # Redirige a LOGIN_URL con next
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            if allow_superuser and getattr(user, "is_superuser", False):
                return view_func(request, *args, **kwargs)

            try:
                perfil = PerfilUsuario.objects.select_related("rol").get(usuario=user)
                nombre = (perfil.rol.nombre or "").strip()
            except PerfilUsuario.DoesNotExist:
                nombre = ""

            if any(nombre.lower() == r.lower() for r in role_names):
                return view_func(request, *args, **kwargs)

            # Usuario autenticado pero sin rol requerido
            if redirect_unauthorized:
                return redirect(redirect_unauthorized)
            return HttpResponseForbidden("Acceso restringido: rol no autorizado")

        return _wrapped

    return decorator


def admin_required(view_func=None, *, redirect_unauthorized=None):
    """Atajo para requerir rol Administrador."""
    dec = role_required("Administrador", redirect_unauthorized=redirect_unauthorized)
    if view_func is None:
        return dec
    return dec(view_func)


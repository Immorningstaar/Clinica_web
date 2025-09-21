from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
import random
from datetime import timedelta

from .models import PasswordResetCode


def index(request):
    return render(request, 'index.html')


def recuperar(request):
    # Renderiza la página de recuperación (front del flujo)
    return render(request, 'recuperar.html')


@require_POST
# Genera y guarda el código (no contamos si existe el correo)
def solicitar_codigo_recuperacion(request):
    correo = request.POST.get("email", "").strip().lower()
    if not correo:
        return JsonResponse({"ok": False, "error": "Correo requerido"}, status=400)

    try:
        user = User.objects.get(email__iexact=correo)
    except User.DoesNotExist:
        # No revelar si existe o no el correo
        return JsonResponse({"ok": True, "mensaje": "Si el correo existe, enviaremos un código."})

    # Generar código de 6 dígitos y guardar con expiración de 10 minutos
    codigo = f"{random.randint(0, 999999):06d}"
    ahora = timezone.now()
    expira = ahora + timedelta(minutes=10)
    PasswordResetCode.objects.create(usuario=user, codigo=codigo, expira_en=expira)

    # Simular envío (log). En DEBUG podríamos devolver el código para pruebas.
    debug = request.META.get("DJANGO_SETTINGS_MODULE") is not None
    data = {"ok": True, "ttl": 600}
    if debug:
        data["codigo_debug"] = codigo
    return JsonResponse(data)


@require_POST
@transaction.atomic
# Valida código vigente y cambia la clave con set_password
def reset_password_con_codigo(request):
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
    # Buscar un código vigente no utilizado
    try:
        obj = (
            PasswordResetCode.objects.select_for_update()
            .filter(usuario=user, codigo=codigo, utilizado=False, expira_en__gte=ahora)
            .latest("creado_en")
        )
    except PasswordResetCode.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Código inválido o expirado"}, status=400)

    user.set_password(nueva)
    user.save(update_fields=["password"])
    obj.utilizado = True
    obj.usado_en = ahora
    obj.save(update_fields=["utilizado", "usado_en"])

    return JsonResponse({"ok": True})



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
    if settings.DEBUG if 'settings' in globals() else True:
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


from django.contrib import admin
from .models import Rol, PerfilUsuario, Paciente, Profesional, Cita, Atencion, Diagnostico, Pago

admin.site.register(Rol)
admin.site.register(PerfilUsuario)
admin.site.register(Paciente)
admin.site.register(Profesional)
admin.site.register(Cita)
admin.site.register(Atencion)
admin.site.register(Diagnostico)
admin.site.register(Pago)
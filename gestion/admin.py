from django.contrib import admin
from .models import Rol, PerfilUsuario, Paciente, Profesional, Cita, Atencion, Diagnostico, Pago

admin.site.register(Rol)
admin.site.register(PerfilUsuario)
admin.site.register(Paciente)
admin.site.register(Profesional)
admin.site.register(Atencion)
admin.site.register(Diagnostico)
admin.site.register(Pago)

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'profesional', 'fecha_hora', 'tipo', 'estado']
    list_filter = ['tipo', 'estado', 'fecha_hora']
    search_fields = ['paciente__usuario__first_name', 'paciente__usuario__last_name', 'motivo']
from django.db import models
from decimal import Decimal

from django.contrib.auth.models import User

# Rol
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # "Administrador", "Paciente", etc.

    def __str__(self):
        return self.nombre

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)  # Evita borrar un rol si hay usuarios con él

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"

# Perfil Pacientes, extendiendo el User de Django
class Paciente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    rut = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=200)
    celular = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}"

# Perfil Profesionales, extendiendo el User de Django
class Profesional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    rut = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='profesionales/', blank=True, null=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.first_name} {self.usuario.last_name} ({self.especialidad})"

# Modelo Citas
class Cita(models.Model):
    TIPO_CHOICES = [
        ("consulta", "Consulta"),
        ("presupuesto", "Presupuesto"),
    ]
    ESTADO_CHOICES = [
        ("Agendada", "Agendada"),
        ("Confirmada", "Confirmada"),
        ("En curso", "En curso"),
        ("Atendida", "Atendida"),
        ("Cancelada", "Cancelada"),
        ("Realizada", "Realizada"),
        ("Pagado", "Pagado"),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, null=True, blank=True)
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Agendada")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="consulta")
    prevision = models.CharField(max_length=100, blank=True, null=True)
    medico_tratante = models.CharField(max_length=200, blank=True, null=True)
    comuna = models.CharField(max_length=100, blank=True, null=True)
    documento = models.FileField(upload_to='documentos/', blank=True, null=True)

    class Meta:
        unique_together = [["fecha_hora", "profesional"]]

    def __str__(self):
        return f"Cita de {self.paciente} con {self.profesional}"

# Modelo Atencion, que ocurre durante una Cita
class Atencion(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    notas = models.TextField()
    indicaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Atención para Cita ID: {self.cita.id}"

# Modelo Diagnostico, resultado de una Atencion
class Diagnostico(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10)  # Ej: "J45.9" (Asma)
    descripcion = models.TextField()

    class Meta:
        # Un código de diagnóstico no se puede repetir para la misma atención
        unique_together = [["atencion", "codigo"]]

    def __str__(self):
        return f"Diagnóstico {self.codigo} para Atención ID: {self.atencion.id}"

# Modelo Pago, asociado a una Cita
class Pago(models.Model):
    METODO_CHOICES = [
        ("Efectivo", "Efectivo"),
        ("Tarjeta", "Tarjeta"),
        ("Transferencia", "Transferencia"),
    ]

    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.monto} para la Cita ID: {self.cita.id}"


# Recuperación de contraseña con código (versión simple y clara)
# Guardamos:
# - usuario: a quién se lo dimos
# - codigo: 6 dígitos
# - expira_en: hasta cuándo sirve
# - utilizado/usado_en: para invalidarlo después del primer uso
# Modelo Presupuesto (reformulado, independiente de Cita)
class Presupuesto(models.Model):
    ESTADO_CHOICES = [
        ("Pendiente", "Pendiente"),
        ("Aprobado", "Aprobado"),
        ("Rechazado", "Rechazado"),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    comuna = models.CharField(max_length=100, blank=True)
    medico_tratante = models.CharField(max_length=200, blank=True)
    prevision = models.CharField(max_length=100, blank=True)
    documento = models.FileField(upload_to='documentos/', blank=True, null=True)
    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Pendiente")
    creado_en = models.DateTimeField(auto_now_add=True)

    def calcular_monto_estimado(self):
        base = Decimal("80000")
        multiplicadores = {
            "fonasa": Decimal("0.7"),
            "isapre": Decimal("1.0"),
            "particular": Decimal("1.2"),
        }
        prev = (self.prevision or "").lower().strip()
        return base * multiplicadores.get(prev, Decimal("1.0"))

    def save(self, *args, **kwargs):
        if self.monto_estimado is None:
            self.monto_estimado = self.calcular_monto_estimado()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Presupuesto #{self.pk} - {self.paciente}"

    class Meta:
        ordering = ["-creado_en"]


class PasswordResetCode(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)
    utilizado = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["usuario", "codigo"]),
            models.Index(fields=["expira_en", "utilizado"]),
        ]
        ordering = ["-creado_en"]  # lo más nuevo arriba, suele ser lo que miramos

    def __str__(self):
        estado = "usado" if self.utilizado else "vigente"
        return f"ResetCode({self.usuario.username}, {self.codigo}, {estado})"

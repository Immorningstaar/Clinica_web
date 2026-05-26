from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import Rol, PerfilUsuario, Profesional

PROFESIONALES = [
    {
        "first_name": "Ana",
        "last_name": "Martínez",
        "email": "anamartinez@bosqueverde.cl",
        "rut": "12345678-5",
        "especialidad": "Cardiología",
        "direccion": "Av. Providencia 1234, Santiago",
        "celular": "+56911111111",
    },
    {
        "first_name": "Carlos",
        "last_name": "López",
        "email": "carloslopez@bosqueverde.cl",
        "rut": "23456789-6",
        "especialidad": "Pediatría",
        "direccion": "Av. Providencia 1234, Santiago",
        "celular": "+56922222222",
    },
    {
        "first_name": "María",
        "last_name": "González",
        "email": "mariagonzalez@bosqueverde.cl",
        "rut": "34567890-7",
        "especialidad": "Dermatología",
        "direccion": "Av. Providencia 1234, Santiago",
        "celular": "+56933333333",
    },
    {
        "first_name": "Pedro",
        "last_name": "Silva",
        "email": "pedrosilva@bosqueverde.cl",
        "rut": "45678901-8",
        "especialidad": "Traumatología",
        "direccion": "Av. Providencia 1234, Santiago",
        "celular": "+56944444444",
    },
]

class Command(BaseCommand):
    help = "Crea 4 profesionales de prueba para el sistema"

    def handle(self, *args, **options):
        rol_profesional, _ = Rol.objects.get_or_create(nombre="Profesional")

        for data in PROFESIONALES:
            if User.objects.filter(email=data["email"]).exists():
                self.stdout.write(self.style.WARNING(
                    f"El usuario {data['email']} ya existe, se omite."
                ))
                continue

            user = User.objects.create_user(
                username=data["email"],
                email=data["email"],
                password="Test1234!",
                first_name=data["first_name"],
                last_name=data["last_name"],
            )

            PerfilUsuario.objects.create(
                usuario=user,
                rol=rol_profesional,
            )

            Profesional.objects.create(
                usuario=user,
                rut=data["rut"],
                especialidad=data["especialidad"],
                direccion=data["direccion"],
                celular=data["celular"],
            )

            self.stdout.write(self.style.SUCCESS(
                f"Profesional creado: Dr(a). {data['first_name']} {data['last_name']} ({data['especialidad']})"
            ))

        self.stdout.write(self.style.SUCCESS("Seed de profesionales completado."))

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Rol, PerfilUsuario, Paciente, Profesional, Cita, Pago


class ModelTests(TestCase):
    def setUp(self):
        self.rol_paciente = Rol.objects.get_or_create(nombre="Paciente")[0]
        self.rol_profesional = Rol.objects.get_or_create(nombre="Profesional")[0]
        self.user_paciente = User.objects.create_user(
            username="paciente@test.cl", email="paciente@test.cl",
            password="Test1234!", first_name="Paco", last_name="Perez"
        )
        self.user_profesional = User.objects.create_user(
            username="dr@test.cl", email="dr@test.cl",
            password="Test1234!", first_name="Dr", last_name="Lopez"
        )
        PerfilUsuario.objects.create(usuario=self.user_paciente, rol=self.rol_paciente)
        PerfilUsuario.objects.create(usuario=self.user_profesional, rol=self.rol_profesional)
        self.paciente = Paciente.objects.create(
            usuario=self.user_paciente, rut="11111111-1",
            fecha_nacimiento="1990-01-01", direccion="Calle 123",
            celular="912345678"
        )
        self.profesional = Profesional.objects.create(
            usuario=self.user_profesional, rut="22222222-2",
            especialidad="Cardiología"
        )

    def test_rol_creation(self):
        self.assertEqual(str(self.rol_paciente), "Paciente")

    def test_paciente_creation(self):
        self.assertEqual(str(self.paciente), "Paco Perez")

    def test_profesional_creation(self):
        self.assertIn("Cardiología", str(self.profesional))

    def test_cita_creation(self):
        from datetime import datetime
        cita = Cita.objects.create(
            paciente=self.paciente, profesional=self.profesional,
            fecha_hora=datetime(2025, 12, 25, 10, 0),
            motivo="Control general"
        )
        self.assertEqual(cita.estado, "Agendada")
        self.assertEqual(cita.tipo, "consulta")

    def test_pago_creation(self):
        from datetime import datetime
        cita = Cita.objects.create(
            paciente=self.paciente, profesional=self.profesional,
            fecha_hora=datetime(2025, 12, 25, 10, 0),
            motivo="Control"
        )
        pago = Pago.objects.create(cita=cita, monto=50000, metodo="Tarjeta")
        self.assertEqual(float(pago.monto), 50000.00)


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@test.cl", email="test@test.cl",
            password="Test1234!"
        )

    def test_login_with_email(self):
        response = self.client.post("/login/", {"email": "test@test.cl", "password": "Test1234!"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_login_invalid_credentials(self):
        response = self.client.post("/login/", {"email": "test@test.cl", "password": "wrong"})
        self.assertEqual(response.status_code, 401)

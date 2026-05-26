from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ..models import Paciente
from .serializers import PacienteSerializer


class PacienteListView(ListAPIView):
    """
    API: Listado de pacientes.

    Requiere autenticación por token.
    Devuelve id, rut, nombre, apellidos, email, fecha_nacimiento, direccion, celular.
    Ordenado por nombre y apellido del usuario.
    """

    serializer_class = PacienteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Paciente.objects.select_related('usuario').order_by(
            'usuario__first_name',
            'usuario__last_name',
        )

from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ..models import Paciente
from .serializers import PacienteSerializer


class PacienteListView(ListAPIView):
    """Entrega el listado de pacientes para consumo externo."""

    serializer_class = PacienteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Se usa select_related para evitar consultas extra al tomar datos del usuario
        return Paciente.objects.select_related('usuario').order_by(
            'usuario__first_name',
            'usuario__last_name',
        )

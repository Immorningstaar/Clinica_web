from rest_framework import serializers

from ..models import Paciente


class PacienteSerializer(serializers.ModelSerializer):
    """Serializa la informacion basica del paciente junto a los datos del usuario."""

    id = serializers.IntegerField(source='usuario.id', read_only=True)
    nombre = serializers.CharField(source='usuario.first_name')
    apellidos = serializers.CharField(source='usuario.last_name')
    email = serializers.EmailField(source='usuario.email')

    class Meta:
        model = Paciente
        fields = [
            'id',
            'rut',
            'nombre',
            'apellidos',
            'email',
            'fecha_nacimiento',
            'direccion',
            'celular',
        ]

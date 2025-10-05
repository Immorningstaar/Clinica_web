from rest_framework import serializers
from .models import Profesional
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfesionalSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Profesional
        fields = ['rut', 'especialidad', 'celular', 'usuario']

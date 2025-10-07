from django.urls import path

from .views import PacienteListView

app_name = 'gestion_api'

urlpatterns = [
    path('pacientes/', PacienteListView.as_view(), name='pacientes-lista'),
]

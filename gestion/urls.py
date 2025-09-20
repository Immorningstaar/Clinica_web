from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # CRUD de usuarios para Administrador
    path("admin/usuarios/", views.gestion_usuarios, name="gestion_usuarios"),
    path(
        "admin/usuarios/<int:user_id>/editar/",
        views.editar_usuario,
        name="editar_usuario",
    ),
    path(
        "admin/usuarios/<int:user_id>/eliminar/",
        views.eliminar_usuario,
        name="eliminar_usuario",
    ),
]

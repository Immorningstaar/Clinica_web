from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # CRUD de usuarios para Administrador (evitar colisión con Django admin)
    path('panel/usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('panel/usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('panel/usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    # Página de recuperación (HTML)
    path('recuperar.html', views.recuperar, name='recuperar_html'),
    path('recuperar/', views.recuperar, name='recuperar'),
    # Recuperación de contraseña (FP-03)
    path('auth/recuperar/solicitar/', views.solicitar_codigo_recuperacion, name='solicitar_codigo_recuperacion'),
    path('auth/recuperar/reset/', views.reset_password_con_codigo, name='reset_password_con_codigo'),
]

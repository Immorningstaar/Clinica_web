from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Recuperación de contraseña (FP-03)
    path('auth/recuperar/solicitar/', views.solicitar_codigo_recuperacion, name='solicitar_codigo_recuperacion'),
    path('auth/recuperar/reset/', views.reset_password_con_codigo, name='reset_password_con_codigo'),
]

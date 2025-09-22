from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profesionales/', views.profesionales, name='profesionales'),
    path('pagos/', views.pagos, name='pagos'),
    path('centros/', views.centro, name='centro'),
    path('admision/', views.admision, name='admision'),
    path('galerias/', views.galerias, name='galerias'),
    path('login/', views.login, name='login'),
    path('perfil/', views.perfil, name='perfil'),
    path('registro/', views.registro, name='registro'),
    path('recuperar/', views.recuperar, name='recuperar'),
]

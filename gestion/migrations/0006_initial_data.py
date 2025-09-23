from django.db import migrations

def crear_datos_iniciales(apps, schema_editor):
    """
    Crea los roles iniciales y un superusuario.
    """

    Rol = apps.get_model('gestion', 'Rol')
    User = apps.get_model('auth', 'User')
    PerfilUsuario = apps.get_model('gestion', 'PerfilUsuario')

    # --- 1. Crear Roles ---
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
    rol_paciente, _ = Rol.objects.get_or_create(nombre='Paciente')
    Rol.objects.get_or_create(nombre='Profesional')

    # --- 2. Crear Superusuario  ---
    if not User.objects.filter(username='superadmin').exists():
        admin_user = User.objects.create_superuser(
            username='superadmin',
            email='admin@bosqueverde.cl',
            password='superadminpassword'
        )

        PerfilUsuario.objects.create(usuario=admin_user, rol=rol_admin)


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_profesional_celular_profesional_direccion_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_datos_iniciales),
    ]

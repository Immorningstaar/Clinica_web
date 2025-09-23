# Clínica Bosque Verde

Repositorio para el desarrollo del proyecto fullstack de la Clínica Bosque Verde, utilizando Django para el backend y Oracle como base de datos.

---
## Requisitos Previos

### 1. Python
Asegúrate de tener instalado **Python 3.12+** en tu sistema.
```bash
python --version
```

### 2. Base de Datos Oracle
Este proyecto requiere una instalación local de **Oracle Database** (se recomienda la versión Express Edition 21c). La base de datos debe estar instalada y en funcionamiento.

---
## Manejo de Secretos (Variables de Entorno)

Para evitar exponer contraseñas y claves secretas en el código, es una buena práctica usar un archivo `.env`.

**1. Instala `python-dotenv`**
```bash
pip install python-dotenv
```
No olvides agregar la dependencia a tu archivo `requirements.txt`:
```bash
pip freeze > requirements.txt
```

**2. Crea el archivo `.env`**
En la raíz del proyecto, crea un archivo llamado `.env` y pega el siguiente contenido, reemplazando los valores:
```env
# Archivo: .env
SECRET_KEY='tu-secret-key-aqui-puedes-generar-una-nueva'
DB_PASSWORD='LA_CONTRASEÑA_DEL_PROYECTO'
```

**3. Asegúrate de que `.env` esté en `.gitignore`**
Abre tu archivo `.gitignore` y añade la línea `.env` para no subir nunca tus secretos al repositorio.

---
## Configuración Inicial (Solo la primera vez)

### 1. Conéctate a Oracle como Administrador
Usa **SQL\*Plus** o **SQL Developer** con el usuario `sys as sysdba`.

### 2. Crea el Usuario para la Aplicación
Ejecuta los siguientes comandos SQL. Reemplaza `"LA_CONTRASEÑA_DEL_PROYECTO"` con la misma contraseña que pusiste en tu archivo `.env`.

```sql
alter session set "_ORACLE_SCRIPT"=true;
create user clinica identified by "LA_CONTRASEÑA_DEL_PROYECTO";
grant connect, resource to clinica;
alter user clinica quota unlimited on users;
```

---
## Instalación y Puesta en Marcha

**1. Clona el Repositorio**
```bash
git clone [https://github.com/Immorningstaar/Clinica_web.git](https://github.com/Immorningstaar/Clinica_web.git)
cd Clinica_web
```

**2. Crea y Activa el Entorno Virtual**
```bash
# Crea el entorno
python -m venv venv
# Activa el entorno (Windows PowerShell)
.\venv\Scripts\activate
```

**3. Instala las Dependencias**
```bash
pip install -r requirements.txt
```

**4. Aplica las Migraciones**
Este comando creará todas las tablas y, gracias a una migración de datos, **insertará los roles y un superusuario por defecto**.
```bash
python manage.py migrate
```

**5. Inicia el Servidor de Desarrollo**
```bash
python manage.py runserver
```

---
## Credenciales de Acceso Iniciales

La migración de datos crea un superusuario por defecto para que todo el equipo pueda empezar a probar. Las credenciales son:

* **Username:** `superadmin`
* **Email:** `admin@bosqueverde.cl`
* **Password:** `superadminpassword`

Existen dos formas de iniciar sesión:

### Login Público (`/login/`)
* **Usuario:** `admin@bosqueverde.cl` (se usa el **Email**)
* **Contraseña:** `superadminpassword`

### Panel de Administración de Django (`/admin/`)
* **Usuario:** `superadmin` (se usa el **Username**)
* **Contraseña:** `superadminpassword`

---
## Cómo Usar

Una vez que el servidor esté corriendo, abre browser en:

**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

Para acceder al panel de administración, ve a:

**[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**

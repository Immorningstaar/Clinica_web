# Clínica Bosque Verde

Repositorio para el desarrollo del proyecto fullstack de la Clínica Bosque Verde, utilizando Django para el backend.

---
## Requisitos Previos

### 1. Python
Asegúrate de tener instalado **Python 3.12+** en tu sistema. Verifícalo con el comando:
```bash
python --version
```

### 2. Base de Datos Oracle
Este proyecto requiere una instalación local de **Oracle Database** (se recomienda la versión Express Edition 21c). La base de datos debe estar instalada y en funcionamiento antes de continuar.

---
## ⚙️ Configuración Inicial (Solo la primera vez)

Antes de ejecutar la aplicación, debes configurar el usuario de la base de datos.

### 1. Conéctate a Oracle como Administrador
Usa una herramienta como **SQL\*Plus** o **SQL Developer** para conectarte a tu base de datos local con privilegios de administrador.
* **Usuario:** `sys as sysdba`
* **Contraseña:** La que definiste durante la instalación de Oracle.

### 2. Crea el Usuario para la Aplicación
Una vez conectado como administrador, ejecuta los siguientes comandos SQL para crear el usuario y darle los permisos necesarios.
```
USER: 'clinica'

PASSWORD: 'ClinicaBV_Orcl21c!Cedro79'
```

```sql
-- Permite la creación de usuarios locales en algunas versiones de Oracle
alter session set "_ORACLE_SCRIPT"=true;

-- Crea el usuario de la aplicación
create user clinica identified by "PASSWORD";

-- Otorga permisos básicos para operar
grant connect, resource to clinica;

-- Asigna espacio de almacenamiento
alter user clinica quota unlimited on users;
```

Una vez ejecutados los comandos, puedes desconectarte de la sesión de administrador.

---
## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos en tu terminal para clonar y ejecutar el proyecto localmente.

**1. Clona el Repositorio**
```bash
git clone [https://github.com/Immorningstaar/Clinica_web.git](https://github.com/Immorningstaar/Clinica_web.git)
cd Clinica_web
```

**2. Crea y Activa el Entorno Virtual**
```bash
# Crea el entorno (sólo la primera vez)
python -m venv venv

# Activa el entorno (cada vez que abras una nueva terminal)
# En Windows PowerShell:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

**3. Instala las Dependencias**
```bash
pip install -r requirements.txt
```
> **Nota para el equipo:** Si instalas una nueva librería, actualiza el archivo con `pip freeze > requirements.txt` y sube el cambio al repositorio.

**4. Aplica las Migraciones de la Base de Datos**
Este comando creará todas las tablas del proyecto en tu base de datos Oracle. **(Asegúrate de haber completado la configuración de Oracle primero)**.

```bash
python manage.py migrate
```

**5. Inicia el Servidor de Desarrollo**
¡Ya estás listo para empezar!

```bash
python manage.py runserver
```

---
## Cómo Usar

Una vez que el servidor esté corriendo, abre tu navegador en:

**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

Verás la página de inicio de la Clínica Bosque Verde.
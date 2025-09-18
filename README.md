# Clínica Bosque Verde

Repositorio para el desarrollo del proyecto fullstack de la Clínica Bosque Verde, utilizando Django para el backend.

---
## Requisitos Previos

Asegúrate de tener instalado **Python 3.12+** en tu sistema. Verifícalo con el comando:
```bash
python --version
```

---
## Instalación y Puesta en Marcha

Sigue estos pasos en tu terminal para clonar y ejecutar el proyecto localmente.

**1. Clona el Repositorio**
```bash
git clone https://github.com/Immorningstaar/Clinica_web.git
cd Clinica_web
```

**2. Crea y Activa el Entorno Virtual**
Este proyecto utiliza un entorno virtual para gestionar sus dependencias.

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
El archivo `requirements.txt` contiene todas las librerías necesarias.

```bash
pip install -r requirements.txt
```
> **Nota para el equipo:** Si instalas una nueva librería, actualiza el archivo con `pip freeze > requirements.txt` y sube el cambio al repositorio.

**4. Aplica las Migraciones de la Base de Datos**
Este comando prepara la base de datos inicial.

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
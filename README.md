# Clínica Bosque Verde 🏥

**Sistema web de gestión clínica** desarrollado con Django.  
Plataforma integral que permite la administración de citas, atenciones médicas, pagos en línea, perfiles de pacientes y profesionales, admisión y presupuestos.

---

## ✨ Funcionalidades

### 🗓️ Reserva de Citas
- Bloques horarios fijos de **30 min** (08:00–18:00)
- Validación cronológica: no fechas pasadas ni horas vencidas el mismo día
- **Disponibilidad en tiempo real** vía AJAX: los slots ocupados se deshabilitan automáticamente en el formulario
- Cancelación por paciente o profesional con confirmación

### 👨‍⚕️ Profesionales
- Perfil con foto, especialidad, dirección y contacto
- Agenda diaria con todas las citas del día
- Botón **"Atender"** → la cita pasa a estado *"En curso"* y redirige a la ficha clínica

### 📋 Ficha Clínica
- Resumen completo del paciente (nombre, RUT, fecha nac., teléfono, dirección, previsión)
- Registro de **Evolución / Síntomas**
- **Diagnóstico** con código CIE y descripción
- **Indicaciones y Recetas**
- Botón **"Finalizar Consulta"** → la cita pasa a estado *"Atendida"*

### 💳 Pago en Línea
- **Boleta detallada** con desglose (consulta base + IVA 19%)
- **Simulación de flujo WebPay**: página intermedia con resumen de la transacción y confirmación
- ID de transacción único (`WEBPAY-{id}-{timestamp}`)
- Historial de pagos por cita

### 📄 Admisión y Presupuestos
- Formulario con **auto-completado** para usuarios autenticados
- **Cálculo automático** según previsión:
  - FONASA → 70% ($56,000)
  - Isapre → 100% ($80,000)
  - Particular → 120% ($96,000)
- Adjuntar orden médica (PDF, JPG, PNG)

### 🔐 Autenticación y Roles
- Login por **email** (no username)
- Recuperación de contraseña con **código de 6 dígitos** + expiración
- **3 roles**: Administrador, Paciente, Profesional
- Perfil editable con cambio de contraseña
- Panel de administración de usuarios (CRUD)

### 👁️ Otras Funcionalidades
- **Clima en vivo** vía Weatherstack API (Santiago)
- **Valor UF del día** vía mindicador.cl
- Diseño **responsive** con Bootstrap 5.3
- Mensajes tipo toast centrados y descartables
- Galería de imágenes del centro médico

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Django 5.2 / Python 3.11+ |
| **Frontend** | HTML5 / CSS3 / JavaScript (jQuery) |
| **UI Framework** | Bootstrap 5.3 |
| **Base de Datos** | SQLite (desarrollo) / Oracle 21c XE (producción) |
| **APIs Externas** | Weatherstack, mindicador.cl |
| **Autenticación** | Django Auth + Token Auth (DRF) |
| **Pagos** | WebPay simulado |
| **Versionado** | Git + GitHub |

---

## ⚙️ Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/clinica-bosque-verde.git
cd clinica-bosque-verde

# 2. Crear y activar entorno virtual
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\activate

# Linux/macOS
# source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env   # Editar con tus claves

# 5. Aplicar migraciones (crea tablas + datos iniciales)
python manage.py migrate

# 6. (Opcional) Poblar profesionales de prueba
python manage.py seed_profesionales

# 7. Iniciar servidor
python manage.py runserver
```

---

## 🔑 Credenciales de Prueba

### Superadministrador
| Campo | Valor |
|-------|-------|
| Email | admin@bosqueverde.cl |
| Contraseña | `superadminpassword` |
| Login | `/login/` (usar email) |

### Profesionales (seed)
Ejecutar `python manage.py seed_profesionales` para crear:

| Nombre | Especialidad | Contraseña |
|--------|-------------|------------|
| Dr(a). Martín Martínez | Cardiología | `Test1234!` |
| Dr(a). Laura López | Pediatría | `Test1234!` |
| Dr(a). Carlos González | Dermatología | `Test1234!` |
| Dr(a). Ana Silva | Traumatología | `Test1234!` |

---

## 🧪 Tests

```bash
python manage.py test
```

El sistema cuenta con **7 tests** que cubren:
- Registro de usuarios con validación de contraseña
- Login por email
- Roles y perfiles
- Flujo de recuperación de contraseña
- CRUD de usuarios

---

## 🗺️ Mapa de Rutas

| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/` | index | Página principal con clima |
| `/login/` | login_page | Login por email |
| `/registro/` | registro | Registro de pacientes/profesionales |
| `/perfil/` | perfil_page | Editar perfil y contraseña |
| `/reservar/` | reservar_cita | Reserva con bloques de 30 min |
| `/profesionales/` | profesionales | Listado con fotos y especialidades |
| `/pago/` | pago | Boleta y pago WebPay |
| `/webpay/<id>/` | webpay_simular | Simulación WebPay |
| `/admision/` | admision | Solicitar presupuesto |
| `/mis-citas/` | mis_citas | Historial de citas del paciente |
| `/panel/agenda/` | agenda_medico | Agenda diaria del doctor |
| `/atencion/<id>/` | registrar_atencion | Ficha clínica |
| `/historial/` | historial_paciente | Historial clínico del paciente |
| `/recuperar/` | recuperar | Recuperación de contraseña |
| `/admin/` | Django Admin | Panel administrativo Django |

---

## 📁 Estructura del Proyecto

```
clinica_web/
├── clinica_project/           # Configuración Django
│   ├── settings.py            # Settings con .env
│   └── urls.py                # URLs raíz
├── gestion/                   # App principal
│   ├── models.py              # 10+ modelos (Cita, Paciente, Profesional, etc.)
│   ├── views.py               # 25+ vistas
│   ├── forms.py               # Formularios de registro y perfil
│   ├── urls.py                # 20+ rutas
│   ├── backends.py            # Auth por email
│   ├── decorators.py          # Decorador admin_required
│   ├── serializers.py         # DRF serializers
│   ├── api/                   # API REST
│   └── management/commands/   # seed_profesionales
├── templates/                 # 15+ templates HTML
│   ├── base.html              # Template base con nav/footer
│   ├── includes/messages.html # Toast centrados
│   └── admin/                 # Templates admin
├── static/                    # Archivos estáticos
│   ├── css/style.css          # Estilos personalizados
│   ├── js/                    # Scripts (reservar, pago, perfil, etc.)
│   └── assets/images/         # Logo e imágenes
└── media/                     # Uploads (fotos, documentos)
```

---

## 🧠 Modelos de Datos

| Modelo | Descripción |
|--------|-------------|
| `Rol` | Administrador, Paciente, Profesional |
| `PerfilUsuario` | Relación User ↔ Rol |
| `Paciente` | Datos del paciente (RUT, fecha nac., dirección, celular) |
| `Profesional` | Datos del profesional (RUT, especialidad, foto, contacto) |
| `Cita` | Consulta con paciente, profesional, fecha, estado |
| `Atencion` | Registro clínico (notas, indicaciones) |
| `Diagnostico` | Código CIE + descripción asociado a una atención |
| `Pago` | Transacción con monto, método y fecha |
| `Presupuesto` | Solicitud de presupuesto con monto estimado |
| `PasswordResetCode` | Código de 6 dígitos para recuperación |

---

## 🚀 Roadmap

- [x] Sistema de autenticación con roles
- [x] Reserva de citas con horarios reales
- [x] Ficha clínica con diagnóstico e indicaciones
- [x] Simulación WebPay con boleta detallada
- [x] Admisión y presupuestos automáticos
- [x] Agenda médica diaria
- [x] Cancelación de citas (paciente/profesional)
- [x] Perfil con foto de doctor
- [ ] Integración WebPay real (Transbank)
- [ ] Notificaciones por correo electrónico
- [ ] Dashboard administrativo con reportes
- [ ] Disponibilidad visual (calendario semanal)

---

## 📄 Licencia

MIT

---

## 👥 Autor

Proyecto desarrollado como portafolio de desarrollo web fullstack con Django.

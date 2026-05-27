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

<table align="center">
  <tr>
    <td align="center"><img width="300" alt="Bloques horarios" src="https://github.com/user-attachments/assets/2ed27d39-a570-4be2-87ab-979957a6abef" /><br><sub>Bloques horarios y formulario</sub></td>
    <td align="center"><img width="300" alt="Validación" src="https://github.com/user-attachments/assets/9911a5a6-5703-447e-a75e-c380f1ea7468" /><br><sub>Validación cronológica</sub></td>
    <td align="center"><img width="300" alt="Cancelación" src="https://github.com/user-attachments/assets/fc92a0b7-3565-4419-b0e1-5af3818b2a52" /><br><sub>Cancelación de citas</sub></td>
  </tr>
</table>

### 👨‍⚕️ Profesionales
- Perfil con foto, especialidad, dirección y contacto
- Agenda diaria con todas las citas del día
- Botón **"Atender"** → la cita pasa a estado *"En curso"* y redirige a la ficha clínica

<table align="center">
  <tr>
    <td align="center"><img width="400" alt="Perfil Profesional" src="https://github.com/user-attachments/assets/c1cfae10-bce6-4661-8bcc-cb888cbe9281" /><br><sub>Perfil público del profesional</sub></td>
    <td align="center"><img width="400" alt="Agenda Diaria" src="https://github.com/user-attachments/assets/4a05a8ff-0cb1-4839-a2bb-6d2461f4af92" /><br><sub>Panel de agenda diaria</sub></td>
  </tr>
</table>

### 📋 Ficha Clínica
- Resumen completo del paciente (nombre, RUT, fecha nac., teléfono, dirección, previsión)
- Registro de **Evolución / Síntomas**
- **Diagnóstico** con código CIE y descripción
- **Indicaciones y Recetas**
- Botón **"Finalizar Consulta"** → la cita pasa a estado *"Atendida"*

<p align="center">
  <img width="600" alt="Ficha Clínica" src="https://github.com/user-attachments/assets/ea2dd0e3-125e-49c8-9ade-c7ff7fa6d5ee" /><br>
  <sub>Vista detallada de la Ficha Clínica</sub>
</p>

### 💳 Pago en Línea
- **Boleta detallada** con desglose (consulta base + IVA 19%)
- **Simulación de flujo WebPay**: página intermedia con resumen de la transacción y confirmación
- ID de transacción único (`WEBPAY-{id}-{timestamp}`)
- Historial de pagos por cita

<table align="center">
  <tr>
    <td align="center"><img width="400" alt="Boleta Detallada" src="https://github.com/user-attachments/assets/370a3882-1e27-4322-a125-697d9413ce64" /><br><sub>Desglose de la boleta</sub></td>
    <td align="center"><img width="400" alt="Simulación WebPay" src="https://github.com/user-attachments/assets/c3c17595-2971-444e-ad2f-6de8b310084a" /><br><sub>Simulación de portal WebPay</sub></td>
  </tr>
</table>

### 📄 Admisión y Presupuestos
- Formulario con **auto-completado** para usuarios autenticados
- **Cálculo automático** según previsión:
  - FONASA → 70% ($56,000)
  - Isapre → 100% ($80,000)
  - Particular → 120% ($96,000)
- Adjuntar orden médica (PDF, JPG, PNG)

<p align="center">
  <img width="600" alt="Admisión y Presupuestos" src="https://github.com/user-attachments/assets/1f802fb4-da1b-466a-8d18-4d218355e1b3" /><br>
  <sub>Formulario de admisión y cálculo automático</sub>
</p>

### 🔐 Autenticación y Roles
- Login por **email** (no username)
- Recuperación de contraseña con **código de 6 dígitos** + expiración
- **3 roles**: Administrador, Paciente, Profesional
- Perfil editable con cambio de contraseña
- Panel de administración de usuarios (CRUD)

<table align="center">
  <tr>
    <td align="center"><img width="250" alt="Login" src="https://github.com/user-attachments/assets/41db931a-166c-49b4-8556-fd57945924a6" /><br><sub>Pantalla de Login</sub></td>
    <td align="center"><img width="250" alt="Recuperación" src="https://github.com/user-attachments/assets/e3174de2-db64-47e6-bdca-cf644a0a30a4" /><br><sub>Recuperación de contraseña</sub></td>
    <td align="center"><img width="250" alt="Panel Admin" src="https://github.com/user-attachments/assets/daa48980-7ee2-4ba8-80f6-dccfdb888cff" /><br><sub>Panel de administración</sub></td>
  </tr>
</table>

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
git clone [https://github.com/tu-usuario/clinica-bosque-verde.git](https://github.com/tu-usuario/clinica-bosque-verde.git)
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

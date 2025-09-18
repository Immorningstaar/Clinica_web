$(document).ready(function () {

    // Función para validar RUT
    function validarRut(rut) {
        if (!/^[0-9]+-[0-9kK]{1}$/.test(rut)) return false;

        const [cuerpo, dv] = rut.split('-');
        let suma = 0;
        let multiplo = 2;

        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo[i]) * multiplo;
            multiplo = multiplo < 7 ? multiplo + 1 : 2;
        }

        const dvCalculado = 11 - (suma % 11);
        const dvReal = dvCalculado === 11 ? '0' : dvCalculado === 10 ? 'K' : dvCalculado.toString();

        return dvReal.toUpperCase() === dv.toUpperCase();
    }

    // Validar el formulario al enviar
    $("#formulario-presupuesto").submit(function (event) {
        event.preventDefault();
        let isValid = true;

        // Limpiar errores
        $(".error").text("");

        // Validación Nombre
        const nombre = $("#nombre").val().trim();
        if (nombre === "" || !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(nombre)) {
            $("#error-nombre").text("Ingrese un nombre válido.");
            isValid = false;
        }

        // Validación Apellidos
        const apellidos = $("#apellidos").val().trim();
        if (apellidos === "" || !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(apellidos)) {
            $("#error-apellidos").text("Ingrese apellidos válidos.");
            isValid = false;
        }

        // Validación RUT
        const rut = $("#rut").val().trim();
        if (!validarRut(rut)) {
            $("#error-rut").text("Ingrese un RUT válido.");
            isValid = false;
        }

        // Validación Fecha
        const fecha = $("#fecha").val();
        const hoy = new Date().toISOString().split('T')[0];
        if (!fecha || fecha > hoy) {
            $("#error-fecha").text("Ingrese una fecha válida.");
            isValid = false;
        }

        // Validación Teléfono
        const telefono = $("#telefono").val().trim();
        if (!/^\d{9,}$/.test(telefono)) {
            $("#error-telefono").text("Ingrese un teléfono válido (mínimo 9 dígitos).");
            isValid = false;
        }

        // Validación Correo
        const correo = $("#correo").val().trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            $("#error-correo").text("Ingrese un correo válido.");
            isValid = false;
        }

        // Validación Archivo (opcional)
        const archivo = $("#orden").val();
        if (archivo) {
            const extensiones = /(\.pdf|\.jpg|\.jpeg|\.png)$/i;
            if (!extensiones.exec(archivo)) {
                $("#error-orden").text("Solo se permiten archivos PDF, JPG o PNG.");
                isValid = false;
            }
        }

        // Si todo es válido
        if (isValid) {
            alert("Formulario enviado correctamente.");
            this.reset(); // Limpiar formulario
        }
    });

});

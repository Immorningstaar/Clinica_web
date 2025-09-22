$(document).ready(function () {
    // Validar fortaleza de contraseña en tiempo real
    $("#password").on("input", function () {
        validatePasswordRequirements($(this).val());
    });


    $("#registroForm").submit(function (event) {
        // ELIMINAMOS event.preventDefault();
        // En su lugar, el return false al final detendrá el envío si hay errores.
        
        let isValid = true;

        $(".error-message").hide();
        $(".form-control").removeClass("is-invalid");

        // Campos obligatorios
        // NOTA: Usamos '#rol' para el select, aunque en HTML el name sea 'rol' y el id sea 'rol'.
        const campos = ["#nombre", "#apellidos", "#rut", "#correo", "#direccion", "#password", "#confirm-password", "#telefono", "#rol"];
        const mensajes = [
            "El nombre es obligatorio.",
            "Los apellidos son obligatorios.",
            "El RUT es obligatorio.",
            "El correo es obligatorio.",
            "La dirección es obligatoria.",
            "La contraseña es obligatoria.",
            "Confirme la contraseña ingresada.",
            "El teléfono es obligatorio.",
            "Seleccione un rol."
        ];

        // Validación de campos vacíos
        campos.forEach((campo, i) => {
            const $campo = $(campo);
            
            // Verificación segura: solo intenta hacer .val().trim() si el elemento existe
            if ($campo.length > 0 && $campo.val().trim() === "") {
                $campo.addClass("is-invalid");
                $campo.next(".error-message").text(mensajes[i]).show();
                isValid = false;
            }
        });
        
        // Validar teléfono (9 dígitos y solo números)
        const telefono = $("#telefono").val().trim();
        if (telefono !== "" && (!/^[0-9]+$/.test(telefono) || telefono.length !== 9)) {
            $("#telefono").addClass("is-invalid");
            $("#telefono").next(".error-message").text("El teléfono debe tener 9 dígitos y solo números.").show();
            isValid = false;
        }

        // Validar email
        if ($("#correo").val().trim() !== "" && !validateEmail($("#correo").val().trim())) {
            $("#correo").addClass("is-invalid");
            $("#correo").next(".error-message").text("El formato del correo no es válido.").show();
            isValid = false;
        }

        // Validar RUT (si no está vacío y cumple formato)
        if ($("#rut").val().trim() !== "" && !validarRut($("#rut").val().trim())) {
            $("#rut").addClass("is-invalid");
            $("#rut").next(".error-message").text("El RUT ingresado no es válido.").show();
            isValid = false;
        }

        // Validar fortaleza de contraseña
        if ($("#password").val().trim() !== "") {
            const passwordValidation = validatePassword($("#password").val());
            if (!passwordValidation.isValid) {
                $("#password").addClass("is-invalid");
                $("#password").next(".error-message").text("La contraseña no cumple con todos los requisitos.").show();
                isValid = false;
            }
        }

        // Validar confirmación de contraseña
        if ($("#confirm-password").val().trim() !== "" &&
            $("#password").val() !== $("#confirm-password").val()) {
            $("#confirm-password").addClass("is-invalid");
            $("#confirm-password").next(".error-message").text("Las contraseñas no coinciden.").show();
            isValid = false;
        }

        // Si es válido, el formulario se envía a Django. Si no, se detiene el envío.
        return isValid; 
        // Eliminamos el alert y el reset de aquí.
    });


    // --- FUNCIONES DE VALIDACIÓN ---

    // Función para validar RUT
    function validarRut(rut) {
        if (!/^[0-9]+-[0-9kK]{1}$/.test(rut)) {
            return false;
        }
        const [cuerpo, dv] = rut.split('-');
        let suma = 0;
        let multiplo = 2;
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo.charAt(i), 10) * multiplo;
            multiplo = multiplo === 7 ? 2 : multiplo + 1;
        }
        const dvEsperado = 11 - (suma % 11);
        const dvCalculado = (dvEsperado === 11) ? '0' : (dvEsperado === 10) ? 'K' : dvEsperado.toString();

        return dv.toUpperCase() === dvCalculado;
    }


    // Función para validar email
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // Función para validar contraseña
    function validatePassword(password) {
        const validation = {
            isValid: true,
            requirements: {
                hasLength: password.length >= 8,
                hasUppercase: /[A-Z]/.test(password),
                hasNumber: /[0-9]/.test(password),
                hasSpecial: /[@$!%*?&]/.test(password)
            }
        };

        validation.isValid = Object.values(validation.requirements).every(req => req === true);
        return validation;
    }

    // Función para mostrar el estado de los requisitos de contraseña (UI)
    function validatePasswordRequirements(password) {
        const validation = validatePassword(password);
        updateRequirementUI("#length-check", validation.requirements.hasLength);
        updateRequirementUI("#uppercase-check", validation.requirements.hasUppercase);
        updateRequirementUI("#number-check", validation.requirements.hasNumber);
        updateRequirementUI("#special-check", validation.requirements.hasSpecial);
    }

    // Función para actualizar la UI de cada requisito
    function updateRequirementUI(selector, isValid) {
        const element = $(selector);
        const icon = element.find("i");

        element.removeClass("valid invalid");
        icon.removeClass("bi-check-circle-fill bi-x-circle-fill");

        if (isValid) {
            element.addClass("valid");
            icon.addClass("bi-check-circle-fill");
        } else {
            element.addClass("invalid");
            icon.addClass("bi-x-circle-fill");
        }
    }
});
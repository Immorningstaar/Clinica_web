$(document).ready(function () {
    $("#loginForm").submit(function (event) {
        event.preventDefault();
        let isValid = true;

        $(".error-message").hide();
        $(".form-control").removeClass("is-invalid");

        const correo = $("#correo").val().trim();
        const clave = $("#clave").val().trim();

        // Validar campo Correo (obligatorio)
        if (correo === "") {
            $("#correo").addClass("is-invalid");
            $("#correo").next(".error-message").text("El correo es obligatorio.").show();
            isValid = false;
        } else if (!validateEmail(correo)) {
            // Validar formato de correo
            $("#correo").addClass("is-invalid");
            $("#correo").next(".error-message").text("El formato del correo no es válido.").show();
            isValid = false;
        }

        // Validar campo Contraseña (obligatorio)
        if (clave === "") {
            $("#clave").addClass("is-invalid");
            $("#clave").next(".error-message").text("La contraseña es obligatoria.").show();
            isValid = false;
        } else {
            // Validar que cumpla los mismos requisitos del registro
            const passwordValidation = validatePassword(clave);
            if (!passwordValidation.isValid) {
                $("#clave").addClass("is-invalid");
                $("#clave").next(".error-message").text("La contraseña no cumple con los requisitos de seguridad.").show();
                isValid = false;
            }
        }

        // Si todo es válido
        if (isValid) {
            alert("Inicio de sesión exitoso.");
            $("#loginForm")[0].reset();
        }
    });

    // Función para validar email
    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    // ✅ Función para validar contraseña (misma que en el registro)
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

        // Verificar si todos los requisitos se cumplen
        validation.isValid = Object.values(validation.requirements).every(req => req === true);

        return validation;
    }
});

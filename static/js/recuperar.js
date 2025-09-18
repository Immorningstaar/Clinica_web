// Recuperación de contraseña (mock local)
// - Paso 1: usuario ingresa correo -> generamos código y lo guardamos en sessionStorage
// - Paso 2: usuario ingresa código y nueva contraseña -> validamos y confirmamos

$(document).ready(function () {
    const CODE_TTL_MS = 10 * 60 * 1000; // 10 minutos

    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
    // Validar requisitos de contraseña
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
        validation.isValid = Object.values(validation.requirements).every(Boolean);
        return validation;
    }
    // Actualizar UI de requisitos
    function updateRequirementUI(selector, ok) {
        const element = $(selector);
        const icon = element.find("i");
        element.removeClass("valid invalid");
        icon.removeClass("bi-check-circle-fill bi-x-circle-fill");
        if (ok) { element.addClass("valid"); icon.addClass("bi-check-circle-fill"); }
        else { element.addClass("invalid"); icon.addClass("bi-x-circle-fill"); }
    }
    // Monitorear entrada de nueva contraseña
    $("#nuevaClave").on("input", function(){
        const v = validatePassword($(this).val());
        updateRequirementUI("#length-check", v.requirements.hasLength);
        updateRequirementUI("#uppercase-check", v.requirements.hasUppercase);
        updateRequirementUI("#number-check", v.requirements.hasNumber);
        updateRequirementUI("#special-check", v.requirements.hasSpecial);
    });

    // Paso 1: solicitar código
    $("#solicitarCodigoForm").on("submit", function(e){
        e.preventDefault();
        const correo = $("#correoRecuperacion").val().trim();
        $("#correoRecuperacion").removeClass("is-invalid");
        $("#correoRecuperacion").next(".error-message").text("").hide();

        if (!validateEmail(correo)) {
            $("#correoRecuperacion").addClass("is-invalid");
            $("#correoRecuperacion").next(".error-message").text("Ingresa un correo válido.").show();
            return;
        }

        // Generar código 6 dígitos y guardar con expiración
        const code = Math.floor(100000 + Math.random()*900000).toString();
        const payload = { code, exp: Date.now() + CODE_TTL_MS };
        sessionStorage.setItem(`reset:${correo}`, JSON.stringify(payload));

        // Mostrar instrucción (en producción, se enviaría por correo)
        $("#info-envio").text(`Te enviamos un código a ${correo}. (Código: ${code})`).show();
        $("#resetForm").show();
        $("#codigo").focus();
    });

    // Paso 2: validar y restablecer
    $("#resetForm").on("submit", function(e){
        e.preventDefault();
        const correo = $("#correoRecuperacion").val().trim();
        const codigo = $("#codigo").val().trim();
        const pass = $("#nuevaClave").val();
        const pass2 = $("#confirmarClave").val();

        $("#codigo, #nuevaClave, #confirmarClave").removeClass("is-invalid");
        $("#resetForm .error-message").text("").hide();
        // Validar código
        const raw = sessionStorage.getItem(`reset:${correo}`);
        if (!raw) {
            $("#codigo").addClass("is-invalid");
            $("#codigo").next(".error-message").text("Vuelve a solicitar el código.").show();
            return;
        } // debería existir
        const data = JSON.parse(raw);
        if (Date.now() > data.exp) {
            $("#codigo").addClass("is-invalid");
            $("#codigo").next(".error-message").text("El código expiró. Solicítalo nuevamente.").show();
            return;
        } // no expiró
        if (codigo !== data.code) {
            $("#codigo").addClass("is-invalid");
            $("#codigo").next(".error-message").text("Código incorrecto.").show();
            return;
        }
        // Validar nueva contraseña
        const v = validatePassword(pass);
        if (!v.isValid) {
            $("#nuevaClave").addClass("is-invalid");
            $("#nuevaClave").nextAll(".error-message:first").text("La contraseña no cumple requisitos.").show();
            return;
        } // es válida
        if (pass !== pass2) {
            $("#confirmarClave").addClass("is-invalid");
            $("#confirmarClave").next(".error-message").text("Las contraseñas no coinciden.").show();
            return;
        }

        // En producción: enviar al backend {correo, nueva contraseña}
        sessionStorage.removeItem(`reset:${correo}`);
        $("#mensajeExito").show();
        setTimeout(() => { window.location.href = 'login.html'; }, 1800);
    });
});


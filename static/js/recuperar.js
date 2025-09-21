// Recuperación de contraseña contra backend
// - Paso 1: backend genera y (simula) envía el código
// - Paso 2: backend valida código y actualiza la contraseña

$(document).ready(function () {
    const CODE_TTL_MS = 10 * 60 * 1000; // referencia de UI (10 min)

    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
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
    function updateRequirementUI(selector, ok) {
        const element = $(selector);
        const icon = element.find("i");
        element.removeClass("valid invalid");
        icon.removeClass("bi-check-circle-fill bi-x-circle-fill");
        if (ok) { element.addClass("valid"); icon.addClass("bi-check-circle-fill"); }
        else { element.addClass("invalid"); icon.addClass("bi-x-circle-fill"); }
    }
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    $("#nuevaClave").on("input", function(){
        const v = validatePassword($(this).val());
        updateRequirementUI("#length-check", v.requirements.hasLength);
        updateRequirementUI("#uppercase-check", v.requirements.hasUppercase);
        updateRequirementUI("#number-check", v.requirements.hasNumber);
        updateRequirementUI("#special-check", v.requirements.hasSpecial);
    });

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

        fetch('/auth/recuperar/solicitar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({ email: correo }).toString()
        }).then(r=>r.json()).then(data=>{
            if (!data.ok) throw new Error(data.error || 'Error al solicitar código');
            const msg = data.codigo_debug ? `Te enviamos un código a ${correo}. (Código: ${data.codigo_debug})` : `Te enviamos un código a ${correo}.`;
            $("#info-envio").text(msg).show();
            $("#resetForm").removeClass('d-none');
            $("#codigo").focus();
        }).catch(err=>{
            $("#correoRecuperacion").addClass("is-invalid");
            $("#correoRecuperacion").next(".error-message").text(err.message).show();
        });
    });

    $("#resetForm").on("submit", function(e){
        e.preventDefault();
        const correo = $("#correoRecuperacion").val().trim();
        const codigo = $("#codigo").val().trim();
        const pass = $("#nuevaClave").val();
        const pass2 = $("#confirmarClave").val();

        $("#codigo, #nuevaClave, #confirmarClave").removeClass("is-invalid");
        $("#resetForm .error-message").text("").hide();

        const v = validatePassword(pass);
        if (!v.isValid) {
            $("#nuevaClave").addClass("is-invalid");
            $("#nuevaClave").nextAll(".error-message:first").text("La contraseña no cumple requisitos.").show();
            return;
        }
        if (pass !== pass2) {
            $("#confirmarClave").addClass("is-invalid");
            $("#confirmarClave").next(".error-message").text("Las contraseñas no coinciden.").show();
            return;
        }

        fetch('/auth/recuperar/reset/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({ email: correo, codigo, password: pass }).toString()
        }).then(r=>r.json()).then(data=>{
            if (!data.ok) throw new Error(data.error || 'No fue posible restablecer');
            $("#mensajeExito").removeClass('d-none');
            setTimeout(() => { window.location.href = 'login.html'; }, 1800);
        }).catch(err=>{
            $("#codigo").addClass("is-invalid");
            $("#codigo").next(".error-message").text(err.message).show();
        });
    });
});

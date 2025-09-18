$(document).ready(function () {
    $("#perfilForm").submit(function (event) {
        event.preventDefault(); 
        let isValid = true;

        $(".error-message").hide();
        $(".form-control").removeClass("is-invalid");

        // --- Validación de campos obligatorios ---
        const direccion = $("#direccion");
        if (direccion.val().trim() === "") {
            direccion.addClass("is-invalid");
            direccion.next(".error-message").text("La dirección es obligatoria.").show();
            isValid = false;
        }

        const telefono = $("#telefono");
        if (telefono.val().trim() === "") {
            telefono.addClass("is-invalid");
            telefono.next(".error-message").text("El teléfono es obligatorio.").show();
            isValid = false;
        }

        // --- Validación para el cambio de contraseña (solo si se intenta cambiar) ---
        const currentPassword = $("#current-password");
        const newPassword = $("#new-password");
        const confirmPassword = $("#confirm-password");

        if (currentPassword.val() || newPassword.val() || confirmPassword.val()) {
            
            if (currentPassword.val().trim() === "") {
                currentPassword.addClass("is-invalid");
                currentPassword.next(".error-message").text("Debes ingresar tu contraseña actual.").show();
                isValid = false;
            }
            if (newPassword.val().trim() === "") {
                newPassword.addClass("is-invalid");
                newPassword.next(".error-message").text("La nueva contraseña es obligatoria.").show();
                isValid = false;
            }
            if (confirmPassword.val().trim() === "") {
                confirmPassword.addClass("is-invalid");
                confirmPassword.next(".error-message").text("Debes confirmar la nueva contraseña.").show();
                isValid = false;
            }

            if (newPassword.val() && confirmPassword.val() && newPassword.val() !== confirmPassword.val()) {
                confirmPassword.addClass("is-invalid");
                confirmPassword.next(".error-message").text("Las contraseñas no coinciden.").show();
                isValid = false;
            }
        }

        if (isValid) {
            alert("Perfil actualizado correctamente.");
            currentPassword.val('');
            newPassword.val('');
            confirmPassword.val('');
        }
    });

});
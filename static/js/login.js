$(document).ready(function () {
    // 1. Manejador del envío del formulario
    $("#loginForm").submit(function (event) {
        
        // **¡CRÍTICO!** Detiene el envío normal del formulario para usar AJAX.
        event.preventDefault(); 
        
        let isValid = true;

        $(".error-message").hide();
        $(".form-control").removeClass("is-invalid");

        // Asegúrate de que los IDs coincidan con tu HTML: #correo y #clave
        const correo = $("#correo").val().trim(); 
        const clave = $("#clave").val().trim();

        // --- VALIDACIONES DE LADO DEL CLIENTE ---
        
        // Validar campo Correo (obligatorio y formato)
        if (correo === "") {
            $("#correo").addClass("is-invalid");
            $("#correo").next(".error-message").text("El correo es obligatorio.").show();
            isValid = false;
        } else if (!validateEmail(correo)) {
            $("#correo").addClass("is-invalid");
            $("#correo").next(".error-message").text("El formato del correo no es válido.").show();
            isValid = false;
        }

        // Validar campo Contraseña (obligatorio y seguridad)
        if (clave === "") {
            $("#clave").addClass("is-invalid");
            $("#clave").next(".error-message").text("La contraseña es obligatoria.").show();
            isValid = false;
        } else {
            const passwordValidation = validatePassword(clave);
            if (!passwordValidation.isValid) {
                $("#clave").addClass("is-invalid");
                $("#clave").next(".error-message").text("La contraseña no cumple con los requisitos de seguridad.").show();
                isValid = false;
            }
        }

        // --- ENVÍO AJAX AL SERVIDOR ---
        if (isValid) {
            $.ajax({
                url: "/login/", // Debe coincidir con la URL de tu vista login_page
                type: "POST",
                data: {
                    // Django espera 'username' (que tú mapeaste a email) y 'password'
                    email: correo,
                    password: clave,
                    // Token de seguridad de Django
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() 
                },
                success: function(response) {
                    // Si el servidor responde 200 OK (según tu vista JsonResponse)
                    alert(response.message); // Muestra el mensaje de éxito de Django
                    window.location.href = '/'; // Redirige al índice
                },
                error: function(xhr, status, error) {
                    // Si el servidor devuelve un error 400 (según tu vista JsonResponse)
                    let errorData = xhr.responseJSON;
                    let errorMessage = errorData && errorData.message ? errorData.message : "Error desconocido al iniciar sesión.";
                    alert(errorMessage); 
                }
            });
        }
    }); // <--- Cierra la función .submit

    // --- FUNCIONES AUXILIARES ---

    // Función para validar email (agregada para que el código funcione)
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

}); // <--- Cierra la función $(document).ready
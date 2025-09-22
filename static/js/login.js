$(document).ready(function () {
    $("#loginForm").submit(function (event) {
        event.preventDefault();

        $(".error-message").hide();
        $(".form-control").removeClass("is-invalid");
        $("#server-error-message").hide();

        const email = $("#email").val().trim();
        const password = $("#password").val().trim();

        let isValid = true;

        // --- VALIDACIONES DE LADO DEL CLIENTE ---
        
        // Validar campo Correo
        if (email === "") {
            $("#email").addClass("is-invalid").next(".error-message").text("El correo es obligatorio.").show();
            isValid = false;
        } else if (!validateEmail(email)) {
            $("#email").addClass("is-invalid").next(".error-message").text("El formato del correo no es válido.").show();
            isValid = false;
        }

        // Validar campo Contraseña
        if (password === "") {
            $("#password").addClass("is-invalid").next(".error-message").text("La contraseña es obligatoria.").show();
            isValid = false;
        }

        if (isValid) {
            $.ajax({
                url: "/login/",
                type: "POST",
                data: {
                    email: email,
                    password: password,
                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    if (response.success) {
                        window.location.href = response.redirect_url;
                    }
                },
                error: function(xhr) {
                    let errorData = xhr.responseJSON;
                    let errorMessage = errorData && errorData.message ? errorData.message : "Error al conectar con el servidor.";
                    $("#server-error-message").text(errorMessage).show();
                }
            });
        }
    });

    function validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
});
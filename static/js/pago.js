$(document).ready(function () {
        $("#pagoForm").submit(function (event) {
            event.preventDefault();
            let isValid = true;

            // Ocultar mensajes de error previos
            $(".error-message").hide();
            $(".form-control").removeClass("is-invalid");

            // Validar número de cita
            const numeroCita = $("#numeroCita").val().trim();
            if (numeroCita === "") {
                $("#numeroCita").addClass("is-invalid");
                $("#numeroCita").next(".error-message").text("El número de cita es obligatorio.").show();
                isValid = false;
            }

            // Validar monto de pago
            const montoPago = $("#montoPago").val().trim();
            if (montoPago === "") {
                $("#montoPago").addClass("is-invalid");
                $("#montoPago").next(".error-message").text("El monto a pagar es obligatorio.").show();
                isValid = false;
            } else if (parseFloat(montoPago) <= 0) {
                $("#montoPago").addClass("is-invalid");
                $("#montoPago").next(".error-message").text("El monto debe ser mayor a cero.").show();
                isValid = false;
            }

            // Validar método de pago
            const metodoPago = $("#metodoPago").val();
            if (metodoPago === "") {
                $("#metodoPago").addClass("is-invalid");
                $("#metodoPago").next(".error-message").text("Debe seleccionar un método de pago.").show();
                isValid = false;
            }

            // Validar correo electrónico
            const correoConfirmacion = $("#correoConfirmacion").val().trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (correoConfirmacion === "") {
                $("#correoConfirmacion").addClass("is-invalid");
                $("#correoConfirmacion").next(".error-message").text("El correo electrónico es obligatorio.").show();
                isValid = false;
            } else if (!emailRegex.test(correoConfirmacion)) {
                $("#correoConfirmacion").addClass("is-invalid");
                $("#correoConfirmacion").next(".error-message").text("Por favor, ingrese un correo electrónico válido.").show();
                isValid = false;
            }

            // Si todos los campos son válidos
            if (isValid) {
                alert("Pago procesado exitosamente. Se ha enviado un comprobante a su correo electrónico.");
                $("#pagoForm")[0].reset();
            }
        });
    });
$(document).ready(function () {
    $("#registroForm").submit(function (event) {
        event.preventDefault();
        let isValid = true;

        $(".error-message").hide();
        $(".form-control, .form-select").removeClass("is-invalid");

        // Campos obligatorios
        const campos = ["#nombre", "#apellidos", "#correo", "#direccion", "#telefono"];
        const mensajes = [
            "El nombre es obligatorio.",
            "Los apellidos son obligatorios.",
            "El correo es obligatorio.",
            "La dirección es obligatoria.",
            "El teléfono es obligatorio.",
            
        ];

        campos.forEach((campo, i) => {
            if ($(campo).val().trim() === "") {
                $(campo).addClass("is-invalid");
                $(campo).next(".error-message").text(mensajes[i]).show();
                isValid = false;
            }
        });

        if (isValid) {
            alert("Usuario registrado correctamente.");
            $("#registroForm")[0].reset();
        }
    });
});

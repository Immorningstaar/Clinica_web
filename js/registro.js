$(document).ready(function () {
        // Validar fortaleza de contraseña en tiempo real
        $("#password").on("input", function() {
            validatePasswordRequirements($(this).val());
        });

    
        $("#registroForm").submit(function (event) {
            event.preventDefault();
            let isValid = true;

            $(".error-message").hide();
            $(".form-control").removeClass("is-invalid");

            // Campos obligatorios
            const campos = ["#nombre", "#apellidos", "#rut", "#correo", "#direccion", "#password", "#confirm-password", "#telefono"];
            const mensajes = [
                "El nombre es obligatorio.",
                "Los apellidos son obligatorios.",
                "El RUT es obligatorio.",
                "El correo es obligatorio.",
                "La dirección es obligatoria.",
                "La contraseña es obligatoria.",
                "Confirme la contraseña ingresada.",
                "El teléfono es obligatorio.",
            ];

            campos.forEach((campo, i) => {
                if ($(campo).val().trim() === "") {
                    $(campo).addClass("is-invalid");
                    $(campo).next(".error-message").text(mensajes[i]).show();
                    isValid = false;
                }
            });

            // Validar email
            if ($("#correo").val().trim() !== "" && !validateEmail($("#correo").val().trim())) {
                $("#correo").addClass("is-invalid");
                $("#correo").next(".error-message").text("El formato del correo no es válido.").show();
                isValid = false;
            }

        

            // Validar contraseña
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

            if (isValid) {
                alert("Usuario registrado correctamente.");
                $("#registroForm")[0].reset();
                // Limpiar los indicadores de contraseña
                $(".requirement").removeClass("valid invalid");
                $(".requirement i").removeClass("bi-check-circle-fill bi-x-circle-fill");
            }
        });

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
            
            // Verificar si todos los requisitos se cumplen
            validation.isValid = Object.values(validation.requirements).every(req => req === true);
            
            return validation;
        }

        // Función para mostrar el estado de los requisitos de contraseña
        function validatePasswordRequirements(password) {
            const validation = validatePassword(password);
            
            // Actualizar la interfaz para cada requisito
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

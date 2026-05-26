$(document).ready(function () {
    function cargarHorasOcupadas() {
        const profesional = $("#profesional").val();
        const fecha = $("#fecha").val();
        if (!profesional || !fecha) return;

        $("#hora option").prop("disabled", false).css("color", "");
        $("#hora").prop("disabled", true);

        $.getJSON("/horas-ocupadas/", { profesional_id: profesional, fecha: fecha })
            .done(function (data) {
                data.ocupadas.forEach(function (hora) {
                    $("#hora option[value='" + hora + "']").prop("disabled", true).css("color", "#ccc");
                });
            })
            .always(function () {
                filtrarHorasPasadas();
                $("#hora").prop("disabled", false);
            });
    }

    function filtrarHorasPasadas() {
        const hoyStr = $("#fecha").attr("min");
        const fechaSel = $("#fecha").val();
        if (fechaSel !== hoyStr) return;

        const ahora = new Date();
        const horaActual = ahora.getHours() * 60 + ahora.getMinutes();

        $("#hora option").each(function () {
            const val = $(this).val();
            if (!val) return;
            const partes = val.split(":");
            const minutos = parseInt(partes[0]) * 60 + parseInt(partes[1]);
            if (minutos <= horaActual) {
                $(this).prop("disabled", true).css("color", "#ccc");
            }
        });
    }

    $("#profesional, #fecha").change(cargarHorasOcupadas);

    $("#reservaForm").submit(function (event) {
        let isValid = true;

        $(".error-message").hide();
        $(".form-control, .form-select").removeClass("is-invalid");

        const profesional = $("#profesional").val();
        if (!profesional) {
            $("#profesional").addClass("is-invalid");
            $("#profesional").next(".error-message").text("Debe seleccionar un profesional.").show();
            isValid = false;
        }

        const fecha = $("#fecha").val();
        if (!fecha) {
            $("#fecha").addClass("is-invalid");
            $("#fecha").next(".error-message").text("Debe seleccionar una fecha.").show();
            isValid = false;
        }

        const hora = $("#hora").val();
        if (!hora) {
            $("#hora").addClass("is-invalid");
            $("#hora").next(".error-message").text("Debe seleccionar un horario.").show();
            isValid = false;
        } else {
            const opt = $("#hora option[value='" + hora + "']");
            if (opt.prop("disabled")) {
                $("#hora").addClass("is-invalid");
                $("#hora").next(".error-message").text("Este horario no está disponible. Seleccione otro.").show();
                isValid = false;
            }
        }

        const motivo = $("#motivo").val().trim();
        if (!motivo) {
            $("#motivo").addClass("is-invalid");
            $("#motivo").next(".error-message").text("El motivo es obligatorio.").show();
            isValid = false;
        }

        return isValid;
    });
});

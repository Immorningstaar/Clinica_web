$(document).ready(function () {
    $(".btn-webpay").on("click", function () {
        $(this).prop("disabled", true).text("Redirigiendo a WebPay...");
    });
});

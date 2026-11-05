document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-excel, .btn-logs").forEach(function (boton) {
        boton.addEventListener("click", function () {
            boton.classList.add("disabled");
            window.setTimeout(function () { boton.classList.remove("disabled"); }, 1200);
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".filtros-danzarines");
    if (form) {
        form.querySelector("input[name='q']").focus();
    }
});

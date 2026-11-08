(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const formulario = document.getElementById('filtroComunicados');
        const busqueda = formulario && formulario.querySelector('input[name="q"]');
        let temporizador;

        if (busqueda) {
            busqueda.addEventListener('input', function () {
                window.clearTimeout(temporizador);
                temporizador = window.setTimeout(function () {
                    formulario.requestSubmit();
                }, 350);
            });
        }
    });
})();

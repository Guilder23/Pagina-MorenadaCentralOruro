// Cierra el sidebar al elegir una opción en pantallas pequeñas.
(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.sidebar-link').forEach(function (enlace) {
            enlace.addEventListener('click', function () {
                document.body.classList.remove('sidebar-abierto');
            });
        });
    });
})();

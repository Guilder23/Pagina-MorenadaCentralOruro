(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.detalle-descripcion a').forEach(function (enlace) {
            enlace.target = '_blank';
            enlace.rel = 'noopener noreferrer';
        });
    });
})();


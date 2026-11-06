(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Carga de forma diferida la fotografía del detalle.
        const foto = document.querySelector('.detalle-foto');
        if (foto) foto.loading = 'lazy';
    });
})();

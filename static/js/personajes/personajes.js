(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Envía la búsqueda al presionar Enter y vuelve a la primera página.
        const buscar = document.getElementById('buscarPersonajes');
        if (!buscar) return;

        buscar.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter') return;
            event.preventDefault();

            const url = new URL(window.location.href);
            if (buscar.value.trim()) url.searchParams.set('q', buscar.value.trim());
            else url.searchParams.delete('q');
            url.searchParams.delete('page');
            window.location.href = url.toString();
        });
    });
})();

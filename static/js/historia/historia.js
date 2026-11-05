(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        const buscar = document.getElementById('buscarHistoria');
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

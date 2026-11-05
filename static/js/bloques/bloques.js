(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const buscar = document.getElementById('buscarBloque');
        const estado = document.getElementById('estadoBloque');
        if (!buscar || !estado) return;

        function aplicarFiltros() {
            const url = new URL(window.location.href);
            const q = buscar.value.trim();
            if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
            if (estado.value) url.searchParams.set('estado', estado.value); else url.searchParams.delete('estado');
            url.searchParams.delete('page');
            window.location.href = url.toString();
        }

        buscar.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                aplicarFiltros();
            }
        });
        estado.addEventListener('change', aplicarFiltros);

        if (buscar.value) {
            buscar.focus();
            buscar.setSelectionRange(buscar.value.length, buscar.value.length);
        }
    });
})();

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const cerrarDup = document.getElementById('cerrarDuplicados');
        if (cerrarDup) {
            cerrarDup.addEventListener('click', function () {
                document.getElementById('panelDuplicados').remove();
            });
        }
        const buscar = document.getElementById('buscarDanzarin');
        const estado = document.getElementById('estadoDanzarin');
        const bloque = document.getElementById('bloqueDanzarin');
        if (!buscar || !estado) return;

        function aplicarFiltros() {
            const url = new URL(window.location.href);
            const q = buscar.value.trim();
            if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
            if (estado.value) url.searchParams.set('estado', estado.value); else url.searchParams.delete('estado');
            if (bloque && bloque.value) url.searchParams.set('bloque', bloque.value); else url.searchParams.delete('bloque');
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
        if (bloque) bloque.addEventListener('change', aplicarFiltros);

        if (buscar.value) {
            buscar.focus();
            buscar.setSelectionRange(buscar.value.length, buscar.value.length);
        }
    });
})();

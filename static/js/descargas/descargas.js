(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Aplica la búsqueda y el filtro por tipo conservando ambos criterios.
        const buscar = document.getElementById('buscarDescargas');
        const tipo = document.getElementById('tipoDescarga');
        if (!buscar || !tipo) return;

        function aplicarFiltros() {
            const url = new URL(window.location.href);
            if (buscar.value.trim()) url.searchParams.set('q', buscar.value.trim());
            else url.searchParams.delete('q');
            if (tipo.value) url.searchParams.set('tipo', tipo.value);
            else url.searchParams.delete('tipo');
            url.searchParams.delete('page');
            window.location.href = url.toString();
        }

        buscar.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter') return;
            event.preventDefault();
            aplicarFiltros();
        });
        tipo.addEventListener('change', aplicarFiltros);
    });
})();

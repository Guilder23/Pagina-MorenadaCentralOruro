(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Aplica la búsqueda y el filtro sin perder el otro criterio.
        const buscar = document.getElementById('buscarCanciones');
        const categoria = document.getElementById('categoriaCancion');
        if (!buscar || !categoria) return;

        function aplicarFiltros() {
            const url = new URL(window.location.href);
            if (buscar.value.trim()) url.searchParams.set('q', buscar.value.trim());
            else url.searchParams.delete('q');
            if (categoria.value) url.searchParams.set('categoria', categoria.value);
            else url.searchParams.delete('categoria');
            url.searchParams.delete('page');
            window.location.href = url.toString();
        }

        buscar.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter') return;
            event.preventDefault();
            aplicarFiltros();
        });
        categoria.addEventListener('change', aplicarFiltros);
    });
})();

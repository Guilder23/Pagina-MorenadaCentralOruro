// Alterna el sidebar compacto en escritorio y abierto/cerrado en móvil.
(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        const boton = document.getElementById('btnToggleSidebar');
        if (!boton) return;

        const escritorio = window.matchMedia('(min-width: 992px)');
        function actualizarEstado() {
            const expandido = escritorio.matches
                ? !document.body.classList.contains('sidebar-colapsado')
                : document.body.classList.contains('sidebar-abierto');
            boton.setAttribute('aria-expanded', String(expandido));
            boton.title = escritorio.matches
                ? (expandido ? 'Colapsar menú lateral' : 'Expandir menú lateral')
                : (expandido ? 'Cerrar menú lateral' : 'Abrir menú lateral');
        }

        actualizarEstado();
        boton.addEventListener('click', function () {
            if (escritorio.matches) {
                document.body.classList.toggle('sidebar-colapsado');
            } else {
                document.body.classList.toggle('sidebar-abierto');
            }
            actualizarEstado();
        });
    });
})();

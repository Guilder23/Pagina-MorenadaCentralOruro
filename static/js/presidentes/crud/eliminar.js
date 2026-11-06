(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Evita envíos repetidos mientras se procesa la eliminación.
        const form = document.getElementById('formEliminarPresidente');
        if (!form) return;

        form.addEventListener('submit', function () {
            const boton = form.querySelector('button[type="submit"]');
            if (!boton) return;

            boton.disabled = true;
            boton.setAttribute('aria-busy', 'true');
            boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Eliminando...';
        });
    });
})();

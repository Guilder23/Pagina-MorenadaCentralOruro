(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Evita enviar más de una vez la confirmación de eliminación.
        const form = document.getElementById('formEliminarDescarga');
        if (!form) return;

        form.addEventListener('submit', function () {
            const submit = form.querySelector('button[type="submit"]');
            if (submit) {
                submit.disabled = true;
                submit.setAttribute('aria-busy', 'true');
            }
        });
    });
})();

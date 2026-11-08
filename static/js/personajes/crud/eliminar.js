(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Evita envíos repetidos mientras se procesa la eliminación.
        const form = document.getElementById('formEliminarPersonaje');
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

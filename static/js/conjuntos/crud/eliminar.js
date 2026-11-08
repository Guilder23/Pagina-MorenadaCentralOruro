(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Impide enviar la confirmación más de una vez.
        const form = document.getElementById('formEliminarConjunto');
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

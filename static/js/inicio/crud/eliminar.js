(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.querySelector('.confirmar-panel');
        if (form) form.querySelector('button[type="submit"]').focus();
    });
})();


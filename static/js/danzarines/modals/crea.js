(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('modalCrearDanzarin');
        if (!modal) return;

        $(modal).on('shown.bs.modal', function () {
            document.getElementById('crearCodigo').focus();
        });

        $(modal).on('hidden.bs.modal', function () {
            document.getElementById('formCrearDanzarin').reset();
        });
    });
})();

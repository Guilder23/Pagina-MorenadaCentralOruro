(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('modalCrearBloque');
        if (!modal) return;

        $(modal).on('shown.bs.modal', function () {
            document.getElementById('crearNombreBloque').focus();
        });

        $(modal).on('hidden.bs.modal', function () {
            document.getElementById('formCrearBloque').reset();
        });
    });
})();

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formEliminarBloque');
        if (!form) return;

        $(document).on('click', '.btn-eliminar-bloque', function () {
            form.setAttribute('action', '/bloques/' + $(this).data('bloque-id') + '/eliminar/');
            $('#eliminarBloqueNombre').text($(this).data('nombre'));
            $('#modalEliminarBloque').modal('show');
        });
    });
})();

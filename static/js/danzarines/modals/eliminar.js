(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formEliminarDanzarin');
        if (!form) return;

        $(document).on('click', '.btn-eliminar-danzarin', function () {
            form.setAttribute('action', '/danzarines/' + $(this).data('danzarin-id') + '/eliminar/');
            $('#eliminarNombre').text($(this).data('nombre'));
            $('#modalEliminarDanzarin').modal('show');
        });
    });
})();

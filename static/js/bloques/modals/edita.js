(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formEditarBloque');
        if (!form) return;

        $(document).on('click', '.btn-editar-bloque', function () {
            const id = $(this).data('bloque-id');
            if (!id) return;

            $.getJSON('/bloques/' + id + '/obtener/')
                .done(function (data) {
                    $('#editNombreBloque').val(data.nombre);
                    $('#editDescripcionBloque').val(data.descripcion);
                    $('#editHabilitadoBloque').prop('checked', !!data.habilitado);
                    form.setAttribute('action', '/bloques/' + data.id + '/editar/');
                    $('#modalEditarBloque').modal('show');
                })
                .fail(function () {
                    alert('No se pudo cargar el bloque.');
                });
        });

        $('#modalEditarBloque').on('hidden.bs.modal', function () {
            form.reset();
            form.setAttribute('action', '');
        });
    });
})();

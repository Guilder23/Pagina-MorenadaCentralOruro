(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formEditarDanzarin');
        if (!form) return;

        $(document).on('click', '.btn-editar-danzarin', function () {
            const id = $(this).data('danzarin-id');
            if (!id) return;

            $.getJSON('/danzarines/' + id + '/obtener/')
                .done(function (data) {
                    $('#editDanzarinId').val(data.id);
                    $('#editCodigo').val(data.codigo);
                    $('#editCi').val(data.ci);
                    $('#editComplementoCi').val(data.complemento_ci);
                    $('#editGenero').val(data.genero);
                    $('#editFechaNacimiento').val(data.fecha_nacimiento);
                    $('#editCorreo').val(data.correo);
                    $('#editBloque').val(data.bloque_id ? String(data.bloque_id) : '');
                    $('#editApellidoPaterno').val(data.apellido_paterno);
                    $('#editApellidoMaterno').val(data.apellido_materno);
                    $('#editPrimerNombre').val(data.primer_nombre);
                    $('#editSegundoNombre').val(data.segundo_nombre);
                    $('#editHabilitado').prop('checked', !!data.habilitado);
                    $('#editUsuario').val(data.usuario || '');
                    $('#editNuevaContrasena').val('');
                    form.setAttribute('action', '/danzarines/' + data.id + '/editar/');
                    $('#modalEditarDanzarin').modal('show');
                })
                .fail(function () {
                    alert('No se pudo cargar el danzarin.');
                });
        });

        $('#modalEditarDanzarin').on('hidden.bs.modal', function () {
            form.reset();
            form.setAttribute('action', '');
        });
    });
})();

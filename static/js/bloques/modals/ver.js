(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        $(document).on('click', '.btn-ver-bloque', function () {
            const id = $(this).data('bloque-id');
            if (!id) return;

            $.getJSON('/bloques/' + id + '/obtener/')
                .done(function (d) {
                    $('#verBloqueIniciales').text((d.nombre || '').slice(0, 2));
                    $('#verBloqueNombre').text(d.nombre);
                    $('#verBloqueEstado')
                        .text(d.estado)
                        .toggleClass('habilitado', !!d.habilitado)
                        .toggleClass('inhabilitado', !d.habilitado);
                    $('#verBloqueDescripcion').text(d.descripcion || '—');
                    $('#verBloqueDanzarines').text(d.total_danzarines);
                    $('#verBloqueCreadoPor').text(d.creado_por || '—');
                    $('#verBloqueFechaCreacion').text(d.fecha_creacion);
                    $('#verBloqueFechaActualizacion').text(d.fecha_actualizacion);
                    $('#modalVerBloque').modal('show');
                })
                .fail(function () {
                    alert('No se pudo cargar el bloque.');
                });
        });
    });
})();

(function () {
    'use strict';

    function texto(valor) {
        return valor ? valor : '—';
    }

    document.addEventListener('DOMContentLoaded', function () {
        $(document).on('click', '.btn-ver-danzarin', function () {
            const id = $(this).data('danzarin-id');
            if (!id) return;

            $.getJSON('/danzarines/' + id + '/obtener/')
                .done(function (d) {
                    $('#verIniciales').text(((d.primer_nombre || '')[0] || '') + ((d.apellido_paterno || '')[0] || ''));
                    $('#verNombreCompleto').text(d.nombre_completo);
                    $('#verEstado')
                        .text(d.estado)
                        .toggleClass('habilitado', !!d.habilitado)
                        .toggleClass('inhabilitado', !d.habilitado);
                    $('#verCodigo').text(d.codigo);
                    $('#verCi').text(d.ci || '—');
                    $('#verBloque').text(texto(d.bloque));
                    $('#verApellidoPaterno').text(texto(d.apellido_paterno));
                    $('#verApellidoMaterno').text(texto(d.apellido_materno));
                    $('#verPrimerNombre').text(texto(d.primer_nombre));
                    $('#verSegundoNombre').text(texto(d.segundo_nombre));
                    $('#verCreadoPor').text(texto(d.creado_por));
                    $('#verFechaCreacion').text(d.fecha_creacion);
                    $('#verFechaActualizacion').text(d.fecha_actualizacion);
                    $('#modalVerDanzarin').modal('show');
                })
                .fail(function () {
                    alert('No se pudo cargar el danzarin.');
                });
        });
    });
})();

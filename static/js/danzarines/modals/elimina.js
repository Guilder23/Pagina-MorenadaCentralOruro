(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formBloquearDanzarin');
        if (!form) return;

        $(document).on('click', '.btn-bloquear-danzarin', function () {
            const id = $(this).data('danzarin-id');
            const habilitado = String($(this).data('habilitado')) === '1';

            form.setAttribute('action', '/danzarines/' + id + '/bloquear/');
            $('#bloquearNombre').text($(this).data('nombre'));
            $('#bloquearTitulo').text(habilitado ? 'Inhabilitar danzarin' : 'Habilitar danzarin');
            $('#bloquearMensaje').text(habilitado
                ? '¿Deseas inhabilitar a este danzarin?'
                : '¿Deseas habilitar nuevamente a este danzarin?');
            $('#bloquearIcono').attr('class', habilitado ? 'fas fa-lock' : 'fas fa-lock-open');
            $('#bloquearConfirmar').text(habilitado ? 'Inhabilitar' : 'Habilitar');
            $('#modalBloquearDanzarin').modal('show');
        });
    });
})();

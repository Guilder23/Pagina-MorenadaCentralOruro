(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formBloquearBloque');
        if (!form) return;

        $(document).on('click', '.btn-bloquear-bloque', function () {
            const id = $(this).data('bloque-id');
            const habilitado = String($(this).data('habilitado')) === '1';

            form.setAttribute('action', '/bloques/' + id + '/bloquear/');
            $('#bloquearBloqueNombre').text($(this).data('nombre'));
            $('#bloquearBloqueTitulo').text(habilitado ? 'Inhabilitar bloque' : 'Habilitar bloque');
            $('#bloquearBloqueMensaje').text(habilitado
                ? '¿Deseas inhabilitar este bloque?'
                : '¿Deseas habilitar nuevamente este bloque?');
            $('#bloquearBloqueIcono').attr('class', habilitado ? 'fas fa-lock' : 'fas fa-lock-open');
            $('#bloquearBloqueConfirmar').text(habilitado ? 'Inhabilitar' : 'Habilitar');
            $('#modalBloquearBloque').modal('show');
        });
    });
})();

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const destinatario = document.getElementById('destinatarioComunicado');
        const grupoBloque = document.getElementById('grupoBloque');
        const bloque = document.getElementById('bloqueComunicado');
        const archivo = document.getElementById('adjuntoComunicado');
        const nombreArchivo = document.getElementById('nombreAdjunto');
        const formulario = document.getElementById('formComunicado');

        function actualizarDestinatario() {
            const requiereBloque = destinatario.value === 'bloque';
            grupoBloque.hidden = !requiereBloque;
            bloque.required = requiereBloque;
            if (!requiereBloque) bloque.value = '';
        }

        destinatario.addEventListener('change', actualizarDestinatario);
        actualizarDestinatario();

        archivo.addEventListener('change', function () {
            const seleccionado = archivo.files[0];
            if (!seleccionado) return;
            nombreArchivo.textContent = seleccionado.name;
            nombreArchivo.classList.remove('error');
            if (seleccionado.size > 10 * 1024 * 1024) {
                nombreArchivo.textContent = 'El archivo supera el límite de 10 MB.';
                nombreArchivo.classList.add('error');
                archivo.value = '';
            }
        });

        formulario.addEventListener('submit', function () {
            const boton = formulario.querySelector('button[type="submit"]');
            boton.disabled = true;
            boton.textContent = 'Guardando comunicado...';
        });
    });
})();

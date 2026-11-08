(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Inicializa la barra de formato y el campo de letra enriquecida.
        const form = document.getElementById('formCancion');
        if (!form) return;

        const editor = form.querySelector('.editor-area');
        const valor = form.querySelector('.editor-valor');
        const formato = form.querySelector('.editor-formato');
        const botonImagen = form.querySelector('.editor-imagen');
        const archivoImagen = form.querySelector('.editor-archivo-imagen');
        const csrf = form.querySelector('[name=csrfmiddlewaretoken]');
        if (!editor || !valor || !formato || !botonImagen || !archivoImagen || !csrf) return;

        // Copia el HTML editado al campo que se envía al servidor.
        const sincronizar = function () {
            valor.value = editor.innerHTML.trim();
        };

        // Aplica negrita, cursiva, enlaces y listas al texto seleccionado.
        form.querySelectorAll('.editor-boton[data-command]').forEach(function (button) {
            button.addEventListener('click', function () {
                editor.focus();
                if (button.dataset.command === 'createLink') {
                    const url = window.prompt('Escribe la URL del enlace:');
                    if (url) document.execCommand('createLink', false, url);
                } else {
                    document.execCommand(button.dataset.command, false, null);
                }
                sincronizar();
            });
        });

        // Cambia el formato del bloque de texto actual.
        formato.addEventListener('change', function () {
            editor.focus();
            document.execCommand('formatBlock', false, this.value);
            sincronizar();
        });

        // Carga imágenes insertadas en la letra y comunica errores al usuario.
        botonImagen.addEventListener('click', function () {
            archivoImagen.click();
        });
        archivoImagen.addEventListener('change', function () {
            if (!this.files[0]) return;

            const datos = new FormData();
            datos.append('imagen', this.files[0]);
            datos.append('csrfmiddlewaretoken', csrf.value);

            fetch(form.dataset.uploadUrl, { method: 'POST', body: datos })
                .then(function (response) {
                    return response.json().then(function (body) {
                        if (!response.ok) {
                            throw new Error(body.error || 'No se pudo subir la imagen.');
                        }
                        return body;
                    });
                })
                .then(function (body) {
                    editor.focus();
                    document.execCommand('insertImage', false, body.url);
                    sincronizar();
                })
                .catch(function (error) {
                    window.alert(error.message || 'No se pudo subir la imagen.');
                });
            this.value = '';
        });

        // Garantiza que los últimos cambios se envíen con el formulario.
        editor.addEventListener('input', sincronizar);
        form.addEventListener('submit', sincronizar);
        sincronizar();
    });
})();

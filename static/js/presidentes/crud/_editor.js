(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Inicialización del formulario y del editor de reseña.
        const form = document.getElementById('formPresidente');
        if (!form) return;

        const editor = form.querySelector('.editor-area');
        const valor = form.querySelector('.editor-valor');
        if (!editor || !valor) return;

        // Sincroniza el contenido visual con el campo enviado al servidor.
        const sync = function () {
            valor.value = editor.innerHTML.trim();
        };

        // Aplica las acciones de formato seleccionadas en la barra.
        form.querySelectorAll('.editor-boton').forEach(function (button) {
            button.addEventListener('click', function () {
                editor.focus();
                if (button.dataset.command === 'createLink') {
                    const url = window.prompt('Escribe la URL del enlace:');
                    if (url) document.execCommand('createLink', false, url);
                } else {
                    document.execCommand(button.dataset.command, false, null);
                }
                sync();
            });
        });

        // Cambia el formato de bloque del texto seleccionado.
        const formato = form.querySelector('.editor-formato');
        formato.addEventListener('change', function () {
            editor.focus();
            document.execCommand('formatBlock', false, this.value);
            sync();
        });

        // Sube imágenes insertadas dentro de la reseña.
        const botonImagen = form.querySelector('.editor-imagen');
        const archivoImagen = form.querySelector('.editor-archivo-imagen');
        botonImagen.addEventListener('click', function () {
            archivoImagen.click();
        });
        archivoImagen.addEventListener('change', function () {
            if (!this.files[0]) return;

            const data = new FormData();
            data.append('imagen', this.files[0]);
            data.append(
                'csrfmiddlewaretoken',
                form.querySelector('[name=csrfmiddlewaretoken]').value
            );

            fetch(form.dataset.uploadUrl, { method: 'POST', body: data })
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
                    sync();
                })
                .catch(function (error) {
                    window.alert(error.message || 'No se pudo subir la imagen.');
                });
            this.value = '';
        });

        // Garantiza que la descripción se envíe al guardar el formulario.
        form.addEventListener('submit', sync);
    });
})();

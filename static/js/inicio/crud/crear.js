(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formCrearPresentacion');
        const editor = form.querySelector('.editor-area');
        const valor = form.querySelector('.editor-valor');

        function sincronizar() {
            valor.value = editor.innerHTML.trim();
        }

        form.querySelectorAll('.editor-boton').forEach(function (boton) {
            boton.addEventListener('click', function () {
                editor.focus();
                if (boton.dataset.command === 'createLink') {
                    const url = window.prompt('Escribe la URL del enlace:');
                    if (url) document.execCommand('createLink', false, url);
                } else {
                    document.execCommand(boton.dataset.command, false, null);
                }
                sincronizar();
            });
        });
        form.querySelector('.editor-formato').addEventListener('change', function () {
            editor.focus();
            document.execCommand('formatBlock', false, this.value);
            sincronizar();
        });
        form.querySelector('.editor-imagen').addEventListener('click', function () {
            form.querySelector('.editor-archivo-imagen').click();
        });
        form.querySelector('.editor-archivo-imagen').addEventListener('change', function () {
            const archivo = this.files[0];
            if (!archivo) return;
            const datos = new FormData();
            datos.append('imagen', archivo);
            datos.append('csrfmiddlewaretoken', form.querySelector('[name=csrfmiddlewaretoken]').value);
            fetch('/inicio/subir-imagen/', { method: 'POST', body: datos })
                .then(function (respuesta) {
                    return respuesta.json().then(function (data) {
                        if (!respuesta.ok) throw new Error(data.error);
                        return data;
                    });
                })
                .then(function (data) {
                    editor.focus();
                    document.execCommand('insertImage', false, data.url);
                    sincronizar();
                })
                .catch(function (error) {
                    alert(error.message || 'No se pudo subir la imagen.');
                });
            this.value = '';
        });
        form.addEventListener('submit', sincronizar);

        const foto = document.getElementById('crearFoto');
        const preview = document.getElementById('crearFotoPreview');
        foto.addEventListener('change', function () {
            const archivo = this.files[0];
            if (!archivo) {
                preview.classList.remove('visible');
                preview.removeAttribute('src');
                return;
            }
            preview.src = URL.createObjectURL(archivo);
            preview.classList.add('visible');
        });
    });
})();

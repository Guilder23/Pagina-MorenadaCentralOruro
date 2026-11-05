(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('formCrearHistoria');
        const editor = form.querySelector('.editor-area');
        const valor = form.querySelector('.editor-valor');
        const sync = function () { valor.value = editor.innerHTML.trim(); };
        form.querySelectorAll('.editor-boton').forEach(function (button) {
            button.addEventListener('click', function () {
                editor.focus();
                if (button.dataset.command === 'createLink') {
                    const url = window.prompt('Escribe la URL del enlace:');
                    if (url) document.execCommand('createLink', false, url);
                } else document.execCommand(button.dataset.command, false, null);
                sync();
            });
        });
        form.querySelector('.editor-formato').addEventListener('change', function () { editor.focus(); document.execCommand('formatBlock', false, this.value); sync(); });
        form.querySelector('.editor-imagen').addEventListener('click', function () { form.querySelector('.editor-archivo-imagen').click(); });
        form.querySelector('.editor-archivo-imagen').addEventListener('change', function () {
            const data = new FormData(); data.append('imagen', this.files[0]); data.append('csrfmiddlewaretoken', form.querySelector('[name=csrfmiddlewaretoken]').value);
            fetch('/historia/subir-imagen/', { method: 'POST', body: data }).then(function (response) { return response.json().then(function (body) { if (!response.ok) throw new Error(body.error); return body; }); }).then(function (body) { editor.focus(); document.execCommand('insertImage', false, body.url); sync(); }).catch(function (error) { alert(error.message || 'No se pudo subir la imagen.'); });
            this.value = '';
        });
        form.addEventListener('submit', sync);
        const foto = document.getElementById('crearFoto');
        foto.addEventListener('change', function () { const preview = document.getElementById('crearFotoPreview'); if (!this.files[0]) { preview.classList.remove('visible'); return; } preview.src = URL.createObjectURL(this.files[0]); preview.classList.add('visible'); });
    });
})();

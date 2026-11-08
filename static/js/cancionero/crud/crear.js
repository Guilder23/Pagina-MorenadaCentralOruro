(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Permite escuchar localmente el audio antes de crear el registro.
        const archivo = document.getElementById('audioCancion');
        const reproductor = document.getElementById('audioCancionPreview');
        if (!archivo || !reproductor) return;

        archivo.addEventListener('change', function () {
            if (!this.files[0]) {
                reproductor.pause();
                reproductor.removeAttribute('src');
                reproductor.hidden = true;
                return;
            }

            reproductor.src = URL.createObjectURL(this.files[0]);
            reproductor.hidden = false;
        });
    });
})();

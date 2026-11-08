(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Muestra una vista previa local de la foto antes de crear el registro.
        const foto = document.getElementById('fotoPersonaje');
        const preview = document.getElementById('fotoPersonajePreview');
        if (!foto || !preview) return;

        foto.addEventListener('change', function () {
            if (!this.files[0]) {
                preview.removeAttribute('src');
                preview.classList.remove('visible');
                return;
            }

            preview.src = URL.createObjectURL(this.files[0]);
            preview.classList.add('visible');
        });
    });
})();

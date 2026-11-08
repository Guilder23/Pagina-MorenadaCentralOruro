(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Actualiza la vista previa cuando se selecciona una foto de reemplazo.
        const foto = document.getElementById('fotoPersonaje');
        const preview = document.getElementById('fotoPersonajePreview');
        if (!foto || !preview) return;

        foto.addEventListener('change', function () {
            if (!this.files[0]) return;

            preview.src = URL.createObjectURL(this.files[0]);
            preview.classList.add('visible');
        });
    });
})();

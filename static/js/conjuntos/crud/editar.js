(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Actualiza la vista previa al escoger una fotografía de reemplazo.
        const foto = document.getElementById('fotoConjunto');
        const preview = document.getElementById('fotoConjuntoPreview');
        if (!foto || !preview) return;

        foto.addEventListener('change', function () {
            if (!this.files[0]) return;

            preview.src = URL.createObjectURL(this.files[0]);
            preview.classList.add('visible');
        });
    });
})();

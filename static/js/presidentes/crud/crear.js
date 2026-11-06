(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Previsualización local de la fotografía antes de crear el registro.
        const foto = document.getElementById('fotoPresidente');
        const preview = document.getElementById('fotoPresidentePreview');
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

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Previsualiza la fotografía seleccionada antes de guardar el conjunto.
        const foto = document.getElementById('fotoConjunto');
        const preview = document.getElementById('fotoConjuntoPreview');
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

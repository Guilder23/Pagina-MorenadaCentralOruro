(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Previsualiza el audio nuevo sin ocultar el archivo ya guardado.
        const archivo = document.getElementById('audioCancion');
        const reproductor = document.getElementById('audioCancionPreview');
        if (!archivo || !reproductor) return;
        const eliminarAudio = document.getElementById('eliminarAudioCancion');

        archivo.addEventListener('change', function () {
            if (!this.files[0]) return;

            if (eliminarAudio) eliminarAudio.checked = false;
            reproductor.src = URL.createObjectURL(this.files[0]);
            reproductor.hidden = false;
        });

        if (eliminarAudio) {
            const audioActual = reproductor.getAttribute('src');
            eliminarAudio.addEventListener('change', function () {
                if (archivo.files[0]) return;
                if (this.checked) {
                    reproductor.pause();
                    reproductor.removeAttribute('src');
                    reproductor.hidden = true;
                } else if (audioActual) {
                    reproductor.src = audioActual;
                    reproductor.hidden = false;
                }
            });
        }
    });
})();

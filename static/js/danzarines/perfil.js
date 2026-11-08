(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const entradaFoto = document.getElementById('id_foto_perfil');
        const vistaFoto = document.getElementById('vistaFotoPerfil');
        const avatar = document.getElementById('avatarIniciales');
        if (!entradaFoto || !vistaFoto) return;

        let urlFoto = '';
        entradaFoto.addEventListener('change', function () {
            const archivo = entradaFoto.files[0];
            if (!archivo) return;
            if (urlFoto) URL.revokeObjectURL(urlFoto);
            urlFoto = URL.createObjectURL(archivo);
            vistaFoto.src = urlFoto;
            vistaFoto.hidden = false;
            if (avatar) avatar.hidden = true;
        });
    });
})();

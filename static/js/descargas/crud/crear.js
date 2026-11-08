(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Muestra el nombre del archivo elegido en el formulario.
        const archivo = document.getElementById('archivoDescarga');
        const nombre = document.getElementById('nombreArchivoSeleccionado');
        const errorTamano = document.getElementById('errorTamanoArchivo');
        const errorTipo = document.getElementById('errorTipoArchivo');
        const ayudaTipo = document.getElementById('ayudaTipoArchivo');
        const formulario = document.getElementById('formDescarga');
        if (!archivo || !nombre) return;

        const obtenerTipo = function () {
            const seleccionado = document.querySelector('input[name="tipo"]:checked');
            return seleccionado ? seleccionado.value : 'pdf';
        };

        const actualizarTipo = function () {
            const tipo = obtenerTipo();
            const esPdf = tipo === 'pdf';
            const extension = esPdf ? '.pdf' : '.mp3';
            const etiqueta = esPdf ? 'Documento PDF' : 'Audio MP3';
            archivo.accept = esPdf ? '.pdf,application/pdf' : '.mp3,audio/mpeg';
            if (ayudaTipo) ayudaTipo.textContent = `Solo se aceptan archivos ${extension} para ${etiqueta}.`;

            const seleccionado = archivo.files[0];
            if (seleccionado && !seleccionado.name.toLowerCase().endsWith(extension)) {
                archivo.value = '';
                nombre.textContent = `Selecciona ${esPdf ? 'un documento PDF' : 'un audio MP3'}`;
                if (errorTipo) {
                    errorTipo.textContent = `El archivo seleccionado no es ${etiqueta}. Selecciona un archivo ${extension}.`;
                    errorTipo.hidden = false;
                }
            } else if (errorTipo) {
                errorTipo.hidden = true;
            }
            validarArchivo();
        };

        const validarArchivo = function () {
            const seleccionado = archivo.files[0];
            const excedeLimite = seleccionado && seleccionado.size > Number(archivo.dataset.maxSize);
            const extension = obtenerTipo() === 'pdf' ? '.pdf' : '.mp3';
            const tipoInvalido = seleccionado && !seleccionado.name.toLowerCase().endsWith(extension);
            if (seleccionado) nombre.textContent = seleccionado.name;
            if (errorTamano) errorTamano.hidden = !excedeLimite;
            if (errorTipo && tipoInvalido) {
                errorTipo.textContent = `Selecciona un archivo ${extension}.`;
                errorTipo.hidden = false;
            }
            return !excedeLimite && !tipoInvalido;
        };

        archivo.addEventListener('change', validarArchivo);
        if (formulario) {
            formulario.addEventListener('submit', function (evento) {
                if (!validarArchivo()) evento.preventDefault();
            });
        }

        const actualizarSeleccion = function () {
            document.querySelectorAll('.tipo-opcion').forEach(function (etiqueta) {
                etiqueta.classList.toggle('is-selected', etiqueta.querySelector('input').checked);
            });
        };
        document.querySelectorAll('input[name="tipo"]').forEach(function (opcion) {
            opcion.addEventListener('change', function () {
                actualizarSeleccion();
                actualizarTipo();
            });
        });
        actualizarSeleccion();
        actualizarTipo();
    });
})();

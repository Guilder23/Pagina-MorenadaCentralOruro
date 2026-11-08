(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        // Muestra el nombre del archivo nuevo antes de reemplazar el actual.
        const archivo = document.getElementById('archivoDescarga');
        const nombre = document.getElementById('nombreArchivoSeleccionado');
        const errorTamano = document.getElementById('errorTamanoArchivo');
        const errorTipo = document.getElementById('errorTipoArchivo');
        const ayudaTipo = document.getElementById('ayudaTipoArchivo');
        const formulario = document.getElementById('formDescarga');
        const marcarEliminarArchivo = document.getElementById('eliminarArchivo');
        const filaArchivoActual = document.getElementById('archivoActualFila');
        const botonEliminarArchivo = document.getElementById('botonEliminarArchivo');
        const estadoEliminarArchivo = document.getElementById('estadoEliminarArchivo');
        const previewArchivo = document.getElementById('archivoSeleccionadoPreview');
        const previewIcono = document.getElementById('archivoSeleccionadoIcono');
        const previewEnlace = document.getElementById('archivoSeleccionadoEnlace');
        const previewTamano = document.getElementById('archivoSeleccionadoTamano');
        const botonQuitarSeleccion = document.getElementById('botonQuitarSeleccion');
        if (!archivo || !nombre) return;
        let urlVistaPrevia = '';

        const obtenerOpcionTipo = function () {
            return document.querySelector('input[name="tipo"]:checked');
        };

        const obtenerTipo = function () {
            const seleccionado = obtenerOpcionTipo();
            return seleccionado ? seleccionado.value : 'pdf';
        };

        const actualizarTipo = function () {
            const tipo = obtenerTipo();
            const esPdf = tipo === 'pdf';
            const extension = esPdf ? '.pdf' : '.mp3';
            const etiqueta = esPdf ? 'Documento PDF' : 'Audio MP3';
            const opcionTipo = obtenerOpcionTipo();
            const tipoOriginal = opcionTipo ? opcionTipo.dataset.currentType : tipo;
            archivo.accept = esPdf ? '.pdf,application/pdf' : '.mp3,audio/mpeg';
            if (ayudaTipo) ayudaTipo.textContent = `Solo se aceptan archivos ${extension} para ${etiqueta}.`;

            const seleccionado = archivo.files[0];
            if (seleccionado && !seleccionado.name.toLowerCase().endsWith(extension)) {
                limpiarSeleccion();
                if (errorTipo) {
                    errorTipo.textContent = `El archivo seleccionado no es ${etiqueta}. Selecciona un archivo ${extension}.`;
                    errorTipo.hidden = false;
                }
            } else if (errorTipo) {
                errorTipo.hidden = true;
            }

            if (errorTipo && !seleccionado && tipo !== tipoOriginal) {
                errorTipo.textContent = `Para cambiar a ${etiqueta}, reemplaza el archivo por uno ${extension}.`;
                errorTipo.hidden = false;
            }
            validarArchivo();
        };

        const validarArchivo = function () {
            const seleccionado = archivo.files[0];
            const excedeLimite = seleccionado && seleccionado.size > Number(archivo.dataset.maxSize);
            const extension = obtenerTipo() === 'pdf' ? '.pdf' : '.mp3';
            const tipoInvalido = seleccionado && !seleccionado.name.toLowerCase().endsWith(extension);
            if (seleccionado) {
                nombre.textContent = seleccionado.name;
                mostrarVistaPrevia(seleccionado);
            }
            if (errorTamano) errorTamano.hidden = !excedeLimite;
            if (errorTipo && tipoInvalido) {
                errorTipo.textContent = `Selecciona un archivo ${extension}.`;
                errorTipo.hidden = false;
            }
            return !excedeLimite && !tipoInvalido;
        };

        const mostrarVistaPrevia = function (seleccionado) {
            if (!previewArchivo) return;
            if (urlVistaPrevia) URL.revokeObjectURL(urlVistaPrevia);
            urlVistaPrevia = URL.createObjectURL(seleccionado);
            if (previewEnlace) {
                previewEnlace.href = urlVistaPrevia;
                previewEnlace.textContent = seleccionado.name;
            }
            if (previewTamano) {
                const tamano = seleccionado.size / (1024 * 1024);
                previewTamano.textContent = `${tamano < 1 ? Math.max(1, Math.round(seleccionado.size / 1024)) + ' KB' : tamano.toFixed(2) + ' MB'}`;
            }
            if (previewIcono) {
                const esAudio = seleccionado.name.toLowerCase().endsWith('.mp3');
                previewIcono.classList.toggle('is-audio', esAudio);
                previewIcono.innerHTML = `<i class="fas ${esAudio ? 'fa-file-audio' : 'fa-file-pdf'}" aria-hidden="true"></i>`;
            }
            previewArchivo.hidden = false;
        };

        const limpiarSeleccion = function () {
            archivo.value = '';
            nombre.textContent = `Selecciona ${obtenerTipo() === 'pdf' ? 'un documento PDF' : 'un audio MP3'}`;
            if (previewArchivo) previewArchivo.hidden = true;
            if (previewEnlace) previewEnlace.removeAttribute('href');
            if (urlVistaPrevia) {
                URL.revokeObjectURL(urlVistaPrevia);
                urlVistaPrevia = '';
            }
            if (errorTamano) errorTamano.hidden = true;
        };

        archivo.addEventListener('change', validarArchivo);
        if (botonQuitarSeleccion) {
            botonQuitarSeleccion.addEventListener('click', function () {
                limpiarSeleccion();
                if (errorTipo) errorTipo.hidden = true;
            });
        }
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

        const actualizarEstadoArchivo = function () {
            if (!marcarEliminarArchivo || !filaArchivoActual || !botonEliminarArchivo) return;
            const marcado = marcarEliminarArchivo.checked;
            filaArchivoActual.classList.toggle('is-removing', marcado);
            botonEliminarArchivo.title = marcado ? 'Cancelar eliminación' : 'Eliminar archivo';
            botonEliminarArchivo.setAttribute(
                'aria-label',
                marcado ? 'Cancelar eliminación del archivo' : 'Eliminar archivo adjunto'
            );
            botonEliminarArchivo.innerHTML = `<i class="fas ${marcado ? 'fa-undo' : 'fa-trash'}" aria-hidden="true"></i>`;
            if (estadoEliminarArchivo) estadoEliminarArchivo.hidden = !marcado;
            if (marcado && errorTipo) errorTipo.hidden = true;
        };

        if (marcarEliminarArchivo && botonEliminarArchivo) {
            botonEliminarArchivo.addEventListener('click', function () {
                marcarEliminarArchivo.checked = !marcarEliminarArchivo.checked;
                actualizarEstadoArchivo();
            });
            archivo.addEventListener('change', function () {
                if (archivo.files.length && marcarEliminarArchivo.checked) {
                    marcarEliminarArchivo.checked = false;
                    actualizarEstadoArchivo();
                }
            });
            actualizarEstadoArchivo();
        }

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

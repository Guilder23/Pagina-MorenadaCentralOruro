(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('modalImportarDanzarines');
        if (!modal) return;

        const form = document.getElementById('formImportarDanzarines');
        const archivo = document.getElementById('importarArchivo');
        const etiqueta = form.querySelector('.custom-file-label');
        const error = document.getElementById('importarError');
        const textoInicial = etiqueta.textContent;
        const MAX_BYTES = 5 * 1024 * 1024;

        archivo.addEventListener('change', function () {
            error.textContent = '';
            etiqueta.textContent = archivo.files.length ? archivo.files[0].name : textoInicial;
        });

        form.addEventListener('submit', function (e) {
            const f = archivo.files[0];
            let mensaje = '';
            if (!f) mensaje = 'Selecciona un archivo Excel (.xlsx).';
            else if (!/\.xlsx$/i.test(f.name)) mensaje = 'El archivo debe tener formato .xlsx.';
            else if (f.size > MAX_BYTES) mensaje = 'El archivo supera el tamaño máximo de 5 MB.';
            if (mensaje) {
                e.preventDefault();
                error.textContent = mensaje;
                return;
            }
            const boton = document.getElementById('btnImportar');
            boton.disabled = true;
            boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Importando...';
        });

        $(modal).on('hidden.bs.modal', function () {
            form.reset();
            etiqueta.textContent = textoInicial;
            error.textContent = '';
        });
    });
})();

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const $ = (id) => document.getElementById(id);

        const formConsulta = $('formConsulta');
        const errorConsulta = $('consultaError');
        const resultado = $('resultadoConsulta');
        const listaWrap = $('listaCoincidencias');
        const lista = $('coincidencias');
        const boton = $('btnConsultar');
        const campo = $('consultaBusqueda');

        campo.addEventListener('input', function () {
            campo.value = campo.value.toUpperCase();
        });

        function mostrarError(mensaje) {
            errorConsulta.querySelector('span').textContent = mensaje || '';
            errorConsulta.classList.toggle('d-none', !mensaje);
        }

        function ocupado(estado) {
            boton.disabled = estado;
            boton.querySelector('.btn-texto').style.opacity = estado ? '.6' : '';
        }

        function mostrarResultado(data) {
            const habilitado = data.habilitado;
            listaWrap.classList.add('d-none');
            resultado.className = 'resultado-consulta ' + (habilitado ? 'ok' : 'no');
            resultado.querySelector('.resultado-icono i').className = 'fas ' + (habilitado ? 'fa-check-circle' : 'fa-times-circle');
            resultado.querySelector('.resultado-nombre').textContent = data.nombre;
            const detalle = resultado.querySelector('.resultado-detalle');
            const partes = [];
            if (data.codigo) partes.push('Código: ' + data.codigo);
            if (data.bloque) partes.push('Bloque: ' + data.bloque);
            detalle.textContent = partes.join(' · ');
            detalle.classList.toggle('d-none', !partes.length);
            const badge = resultado.querySelector('.badge-estado');
            badge.className = 'badge-estado ' + (habilitado ? 'habilitado' : 'inhabilitado');
            badge.textContent = habilitado ? '¡Habilitado!' : 'No habilitado';
            resultado.querySelector('.resultado-texto').textContent = habilitado
                ? 'Fraterno Activo 2026'
                : 'Verifique sus datos. Si sus datos son correctos pero no figura en la nómina, apersónese a oficinas del Directorio con sus descargos para su regularización.';
        }

        function mostrarLista(data) {
            lista.innerHTML = '';
            data.coincidencias.forEach(function (c) {
                const li = document.createElement('li');
                const opcion = document.createElement('button');
                opcion.type = 'button';
                opcion.className = 'coincidencia';
                opcion.setAttribute('role', 'option');
                opcion.textContent = c.nombre;
                opcion.addEventListener('click', function () { elegir(c.id); });
                li.appendChild(opcion);
                lista.appendChild(li);
            });
            if (data.truncado) {
                const aviso = document.createElement('li');
                aviso.className = 'coincidencia-aviso';
                aviso.textContent = 'Hay más resultados. Escribe más datos de tu nombre para acotar la búsqueda.';
                lista.appendChild(aviso);
            }
            listaWrap.classList.remove('d-none');
        }

        function consultar(url, datos, alResponder) {
            ocupado(true);
            fetch(url, { method: 'POST', body: datos, credentials: 'same-origin' })
                .then(function (resp) {
                    return resp.json().catch(function () { return { ok: false, error: 'Respuesta inesperada del servidor.' }; });
                })
                .then(function (data) {
                    if (!data.ok) {
                        mostrarError(data.error || 'No se pudo realizar la consulta.');
                        return;
                    }
                    alResponder(data);
                })
                .catch(function () {
                    mostrarError('No se pudo conectar con el servidor. Intenta nuevamente.');
                })
                .finally(function () { ocupado(false); });
        }

        function nuevosDatos() {
            const datos = new FormData();
            datos.append('csrfmiddlewaretoken', formConsulta.querySelector('[name=csrfmiddlewaretoken]').value);
            return datos;
        }

        function elegir(id) {
            mostrarError('');
            const url = formConsulta.dataset.estadoUrl.replace(/0\/$/, id + '/');
            consultar(url, nuevosDatos(), mostrarResultado);
        }

        formConsulta.addEventListener('submit', function (e) {
            e.preventDefault();
            mostrarError('');
            resultado.classList.add('d-none');
            listaWrap.classList.add('d-none');

            const busqueda = campo.value.trim().toUpperCase();
            if (!busqueda) {
                mostrarError('Ingresa tu código o tu nombre.');
                campo.focus();
                return;
            }

            const datos = nuevosDatos();
            datos.append('busqueda', busqueda);
            consultar(formConsulta.action, datos, function (data) {
                if (data.multiple) mostrarLista(data); else mostrarResultado(data);
            });
        });
    });
})();

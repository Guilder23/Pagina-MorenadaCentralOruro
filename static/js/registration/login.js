(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const $ = (id) => document.getElementById(id);

        function mostrarError(caja, mensaje) {
            if (!caja) return;
            caja.querySelector('span').textContent = mensaje || '';
            caja.classList.toggle('d-none', !mensaje);
        }

        function ocupado(boton, estado) {
            boton.disabled = estado;
            boton.querySelector('.btn-texto').style.opacity = estado ? '.6' : '';
        }

        // Contraseña visible
        const clave = $('id_password');
        const verClave = $('btnMostrarClave');
        verClave.addEventListener('click', function () {
            const visible = clave.type === 'text';
            clave.type = visible ? 'password' : 'text';
            verClave.querySelector('i').className = visible ? 'fas fa-eye' : 'fas fa-eye-slash';
        });

        // Login: validación en danzarin; Enter envía el formulario de forma nativa
        const formLogin = $('formLogin');
        formLogin.addEventListener('submit', function (e) {
            const usuario = $('id_username');
            const pass = $('id_password');
            let valido = true;
            [[usuario, 'Ingresa tu usuario.'], [pass, 'Ingresa tu contraseña.']].forEach(function (par) {
                const campo = par[0];
                const vacio = !campo.value.trim();
                campo.classList.toggle('is-invalid', vacio);
                formLogin.querySelector('[data-error-for="' + campo.id + '"]').textContent = vacio ? par[1] : '';
                if (vacio && valido) { campo.focus(); }
                if (vacio) valido = false;
            });
            if (!valido) {
                e.preventDefault();
                return;
            }
            ocupado($('btnLogin'), true);
        });
        formLogin.querySelectorAll('input.form-control').forEach(function (campo) {
            campo.addEventListener('input', function () {
                campo.classList.remove('is-invalid');
                const msg = formLogin.querySelector('[data-error-for="' + campo.id + '"]');
                if (msg) msg.textContent = '';
            });
        });
    });
})();
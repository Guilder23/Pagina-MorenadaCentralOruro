(function () {
    'use strict';

    // Cierra automáticamente las alertas de éxito
    window.setTimeout(function () {
        if (window.jQuery) {
            window.jQuery('.app-alert.alert-success').alert('close');
        }
    }, 5000);
})();

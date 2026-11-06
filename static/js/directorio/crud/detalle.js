(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    $("#modalPersona").on("show.bs.modal", function (event) {
      document.getElementById("personaSeccion").value =
        event.relatedTarget.dataset.seccion;
    });
  });
})();

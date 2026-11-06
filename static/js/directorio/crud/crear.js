(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    const foto = document.getElementById("crearFoto");
    const preview = document.getElementById("crearFotoPreview");
    if (!foto || !preview) return;
    foto.addEventListener("change", function () {
      const archivo = this.files[0];
      if (!archivo) {
        preview.classList.remove("visible");
        preview.removeAttribute("src");
        return;
      }
      preview.src = URL.createObjectURL(archivo);
      preview.classList.add("visible");
    });
  });
})();

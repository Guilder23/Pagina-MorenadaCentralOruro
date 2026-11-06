(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    const foto = document.getElementById("editFoto");
    const preview = document.getElementById("editFotoPreview");
    if (!foto || !preview) return;
    foto.addEventListener("change", function () {
      const archivo = this.files[0];
      if (!archivo) return;
      preview.src = URL.createObjectURL(archivo);
      preview.classList.add("visible");
    });
  });
})();

(function () {
  "use strict";
  const input = document.getElementById("crearPersonaFoto");
  const preview = document.getElementById("crearPersonaFotoPreview");
  if (input && preview)
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (file) {
        preview.src = URL.createObjectURL(file);
        preview.classList.add("visible");
      }
    });
})();

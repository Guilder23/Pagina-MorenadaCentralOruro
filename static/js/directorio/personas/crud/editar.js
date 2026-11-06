(function () {
  "use strict";
  const input = document.getElementById("editarPersonaFoto");
  const preview = document.getElementById("editarPersonaFotoPreview");
  if (input && preview)
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (file) {
        preview.src = URL.createObjectURL(file);
        preview.classList.add("visible");
      }
    });
})();

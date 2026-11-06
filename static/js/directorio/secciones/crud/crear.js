(function () {
  "use strict";
  const input = document.getElementById("crearSeccionFoto");
  const preview = document.getElementById("crearSeccionFotoPreview");
  if (input && preview)
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (file) {
        preview.src = URL.createObjectURL(file);
        preview.classList.add("visible");
      }
    });
})();

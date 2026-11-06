(function () {
  "use strict";
  const input = document.getElementById("editarSeccionFoto");
  const preview = document.getElementById("editarSeccionFotoPreview");
  if (input && preview)
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (file) {
        preview.src = URL.createObjectURL(file);
        preview.classList.add("visible");
      }
    });
})();

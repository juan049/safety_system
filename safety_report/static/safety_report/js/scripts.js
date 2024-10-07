//Defino el script para subir foto de corrección
uploadImageFormButton = document.querySelectorAll(".upload-form-button"); //Agrego event listener a cada uno
uploadImageFormButton.forEach((button) => {
  button.addEventListener("click", (e) => {
    console.log("Boton");
  });
});

// Script para poner el año
function setCurrentYear() {
  const yearElement = document.getElementById("year-element");
  const currentYear = new Date().getFullYear(); // Obtiene el año actual

  if (yearElement) {
    yearElement.innerText = currentYear; // Inserta el año en el elemento
  }
}

// Event listener para que todo cargue
document.addEventListener("DOMContentLoaded", (event) => {
  setCurrentYear();
});

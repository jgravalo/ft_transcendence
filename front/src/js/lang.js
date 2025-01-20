function changeLanguage(lang) {
    // Update the flag in the dropdown button
    document.getElementById("currentFlag").src = `/src/img/${lang}.png`;

    // Save the selected language in localStorage
    localStorage.setItem("selectedLanguage", lang);

    // Fetch translations from the backend
    fetch(`/api/get-translations?lang=${lang}`)
        .then(response => response.json())
        .then(translations => {
            updateTexts(translations);
        })
        .catch(error => console.error("Error fetching translations:", error));
}

function updateTexts(translations) {
    // Find all elements with the data-i18n attribute
    document.querySelectorAll("[data-i18n]").forEach(element => {
        const key = element.getAttribute("data-i18n");
        if (translations[key]) {
            element.innerText = translations[key];
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const savedLang = localStorage.getItem("selectedLanguage") || "es";
    changeLanguage(savedLang); 
});

function changeLanguage(lang) {
    console.log(`Changing language to: ${lang}`);
    
    // Update the flag in the dropdown button
    const currentFlag = document.getElementById("currentFlag");
    currentFlag.src = `./img/${lang}.svg`;

    // Save the selected language in localStorage
    localStorage.setItem("selectedLanguage", lang);

    // Fetch translations from the backend
    fetch(base + ":8000" + `/get-translations?lang=${lang}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(translations => {
            updateTexts(translations);
        })
        .catch(error => {
            console.error("Error fetching translations:", error);
        });
}

function updateTexts(translations) {
    
    // Find all elements with the data-i18n attribute
    const elements = document.querySelectorAll("[data-i18n]");
    
    elements.forEach(element => {
        const key = element.getAttribute("data-i18n");
        if (translations[key]) {
            element.innerText = translations[key];
        } else {
            console.warn(`No translation found for key: ${key}`);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const savedLang = localStorage.getItem("selectedLanguage") || "en";
    changeLanguage(savedLang); 
});
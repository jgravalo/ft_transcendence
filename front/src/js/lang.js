function changeLanguage(lang) {
    console.log(`Changing language to: ${lang}`);
    
    // Update the flag in the dropdown button
    const currentFlag = document.getElementById("currentFlag");
    currentFlag.src = `./img/${lang}.svg`;

    // Save the selected language in localStorage
    localStorage.setItem("selectedLanguage", lang);
    console.log(`Language saved in localStorage: ${lang}`);

    // Fetch translations from the backend
    fetch(base + ":8000" + `/get-translations?lang=${lang}`)
        .then(response => {
            console.log(`Fetch response status: ${response.status}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(translations => {
            console.log("Fetched translations:", translations);
            updateTexts(translations);
        })
        .catch(error => {
            console.error("Error fetching translations:", error);
        });
}

function updateTexts(translations) {
    console.log("Updating texts with translations:", translations);
    
    // Find all elements with the data-i18n attribute
    const elements = document.querySelectorAll("[data-i18n]");
    console.log(`Found ${elements.length} elements with data-i18n attribute.`);
    
    elements.forEach(element => {
        const key = element.getAttribute("data-i18n");
        console.log(`Updating element with key: ${key}`);
        if (translations[key]) {
            element.innerText = translations[key];
            console.log(`Updated text to: ${translations[key]}`);
        } else {
            console.warn(`No translation found for key: ${key}`);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const savedLang = localStorage.getItem("selectedLanguage") || "en";
    console.log(`DOMContentLoaded: Saved language is ${savedLang}`);
    changeLanguage(savedLang); 
});
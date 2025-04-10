/*
//Original buttons to save the original content
let originalLeftButton;
let originalMiddleButton;
let originalRightButton;
let hasSwitchedToOnline = false;


function bindHomeEvents() {
    const playOnlineBtn = document.getElementById("middle-button");
	if (playOnlineBtn) {
        playOnlineBtn.addEventListener("click", handleOnlineClick);
	}
}

//Button navigation for home page
function handleOnlineClick() {
    if (hasSwitchedToOnline) return;
    hasSwitchedToOnline = true;

    originalLeftButton = document.getElementById('left-button').innerHTML;
    originalMiddleButton = document.getElementById('middle-button').innerHTML;
    originalRightButton = document.getElementById('right-button').innerHTML;

    let leftButton = document.getElementById('left-button');
    let middleButton = document.getElementById('middle-button');
    let rightButton = document.getElementById('right-button');

    leftButton.innerHTML = `
    <h2 class="mode-title" data-i18n="home.return.title">🔙 Back</h2>`;
    leftButton.onclick = resetButtons;
    
    middleButton.innerHTML = `
    <h2 class="mode-title" data-i18n="home.guest.title">👤 Play as Guest</h2>
    <p class="mode-sub" data-i18n="home.guest.description">Jump into a quick match — no login needed</p>`;
    middleButton.onclick = () => fetchLink('/game/remote/guest/');
    
    rightButton.innerHTML = `
    <h2 class="mode-title" data-i18n="home.user.title">🔐 Log In to Play</h2>
    <p class="mode-sub" data-i18n="home.user.description">Save your stats, progress, and compete with others</p>`;
    rightButton.onclick = () => fetchLink('/game/remote/user/');

    changeLanguage(localStorage.getItem("selectedLanguage") || "en");
}

function resetButtons() {

    hasSwitchedToOnline = false;

    const leftButton = document.getElementById('left-button');
    const middleButton = document.getElementById('middle-button');
    const rightButton = document.getElementById('right-button');

    leftButton.innerHTML = originalLeftButton;
    middleButton.innerHTML = originalMiddleButton;
    rightButton.innerHTML = originalRightButton;
}

//Tab navigation for dashboard
function showGameOptions(mode) {
    const leftButton = document.getElementById('left-button');
    const middleButton = document.getElementById('middle-button');
    const rightButton = document.getElementById('right-button');
    
    const originalLeftButton = leftButton.innerHTML;
    const originalMiddleButton = middleButton.innerHTML;
    const originalRightButton = rightButton.innerHTML;
    
    addAct
}
*/

//Tab navigation for dashboard
function showTab(tabId, button) {
	// Hide all tab contents
	document.querySelectorAll('.tab-content').forEach(div => {
		div.classList.add('hidden');
	});

	// Show selected tab
	document.getElementById(tabId).classList.remove('hidden');

	// Only activate active on the right tab button
	document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
	if (button) button.classList.add('active');
}
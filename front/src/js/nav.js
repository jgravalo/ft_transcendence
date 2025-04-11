//Tab navigation for dashboard
function showTab(tabId, button) {
	// Hide all tab contents
	document.querySelectorAll('.tab-content').forEach(div => {div.classList.add('hidden');});

	// Show selected tab
	document.getElementById(tabId).classList.remove('hidden');

	// Only activate active on the right tab button
	document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
	if (button) button.classList.add('active');

    paginateTab(tabId); // Refresh pagination on tab switch
}

function paginateTab(tabId, itemsPerPage = 5) {
	const container = document.getElementById(tabId);
	if (!container) return;

	const items = container.querySelectorAll('.tab-item');
	const pagination = container.querySelector('.pagination');
	if (!pagination) return;

	let currentPage = 1;
	const totalPages = Math.ceil(items.length / itemsPerPage);

	function renderPage(page) {
		currentPage = page;

		items.forEach((item, i) => {
			item.style.display = (i >= (page - 1) * itemsPerPage && i < page * itemsPerPage) ? '' : 'none';
		});

		renderPaginationControls();
	}

	function renderPaginationControls() {
		pagination.innerHTML = '';

		for (let i = 1; i <= totalPages; i++) {
			const btn = document.createElement('button');
			btn.textContent = i;
			btn.className = i === currentPage ? 'active' : '';
			btn.onclick = () => renderPage(i);
			pagination.appendChild(btn);
		}
	}
	renderPage(1);
}

function setupProfilePagination() {
	const activeTabButton = document.querySelector('.tab.active');
	if (activeTabButton) {
		const tabId = activeTabButton.dataset.tabId;
		if (tabId) {
			showTab(tabId, activeTabButton);
		}
	}
}

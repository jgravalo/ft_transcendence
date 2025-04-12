function joinTournament(tournamentId) {
    const btn = document.getElementById(`tournament-join-btn-${tournamentId}`);

    fetch(base + `/api/game/tournament/join/?tournament=${tournamentId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.error === "Success") {
            // Replace button and status manually
            const actions = document.getElementById(`tournament-actions-${tournamentId}`);
            const status = document.getElementById(`tournament-status-${tournamentId}`);
            if (actions)
                actions.innerHTML = `<button id="tournament-leave-btn-${tournamentId}" class="link block-btn" onclick="leaveTournament('${tournamentId}')" data-i18n="profile.tournaments.leave">🚪 Leave Room</button>`;
            if (status)
                status.innerHTML = `<span data-i18n="profile.tournaments.joined">Room Joined. Waiting for other players...</span>`;
        } else {
            alert(data.error);
            if (btn) {
                btn.disabled = false;
                btn.innerText = '⚔️ Join Room';
            }
        }
        changeLanguage(localStorage.getItem("selectedLanguage") || "en"); // Update the texts based on the language
    })
    .catch(err => {
        alert("Error: " + err.message);
        if (btn) {
            btn.disabled = false;
            btn.innerText = '⚔️ Join Room';
        }
    });
}

function leaveTournament(tournamentId) {
    const btn = document.getElementById(`tournament-leave-btn-${tournamentId}`);

    fetch(base + `/api/game/tournament/leave/?tournament=${tournamentId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'X-CSRFToken': getCSRFToken()
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.error === "Success") {
            const actions = document.getElementById(`tournament-actions-${tournamentId}`);
            const status = document.getElementById(`tournament-status-${tournamentId}`);
            if (actions)
                actions.innerHTML = `<button id="tournament-join-btn-${tournamentId}" class="link" onclick="joinTournament('${tournamentId}')" data-i18n="profile.tournaments.join">⚔️ Join Room</button>`;
            if (status)
                status.innerHTML = `<span data-i18n="profile.tournaments.notjoined">Press Join Room to join the tournament</span>`;
        } else {
            alert(data.error);
            if (btn) {
                btn.disabled = false;
                btn.innerText = '🚪 Leave Room';
            }
        }
        changeLanguage(localStorage.getItem("selectedLanguage") || "en"); // Update the texts based on the language
    })
    .catch(err => {
        alert("Error: " + err.message);
        if (btn) {
            btn.disabled = false;
            btn.innerText = '🚪 Leave Room';
        }
    });
}

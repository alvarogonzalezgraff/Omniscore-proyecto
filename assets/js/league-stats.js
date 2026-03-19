
// Logic for displaying league stats
// Data is now loaded from separate files in assets/js/leagues/

function showLeague(league) {
    // Update tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    // Safety check just in case logic is called before buttons load
    const pressedBtn = document.querySelector(`.tab-btn[onclick="showLeague('${league}')"]`);
    if (pressedBtn) pressedBtn.classList.add('active');

    // Access global leagueData
    const data = window.leagueData[league];
    if (!data) {
        console.error(`Data for league ${league} not found!`);
        return;
    }

    const container = document.getElementById('league-content');

    // Updated header to 25/26
    let html = `
        <div class="stats-grid-layout">
            <div class="left-col">
                <div class="stats-table-container">
                    <div class="card-header">Clasificación ${data.name} (Temporada 25/26)</div>
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>Pos</th>
                                <th>Equipo</th>
                                <th>PJ</th>
                                <th>PG</th>
                                <th>PE</th>
                                <th>PP</th>
                                <th>Goles</th>
                                <th>Dif.</th>
                                <th>Pts</th>
                                <th>Forma</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.standings.map(team => `
                                <tr>
                                    <td>${team.pos}</td>
                                    <td>
                                        <div class="team-cell">
                                            ${team.logo
            ? `<img src="${team.logo}" alt="${team.team}" class="team-logo-img" style="width:24px;height:24px;object-fit:contain;">`
            : `<div class="team-logo">${team.team.substring(0, 1)}</div>`
        }
                                            <span>${team.team}</span>
                                        </div>
                                    </td>
                                    <td>${team.played}</td>
                                    <td>${team.won}</td>
                                    <td>${team.drawn}</td>
                                    <td>${team.lost}</td>
                                    <td>${team.gf}:${team.ga}</td>
                                    <td>${team.gf - team.ga}</td>
                                    <td><strong>${team.points}</strong></td>
                                    <td>
                                        ${team.form ? team.form.map(f => {
            const map = { 'W': 'G', 'D': 'E', 'L': 'P' };
            return `<span class="form-badge form-${f}">${map[f] || f}</span>`;
        }).join('') : '-'}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <div class="stats-table-container">
                    <div class="card-header">Resultados Recientes</div>
                    ${data.results[0] && data.results[0].matchweek ?
            // New structured format (Matchweeks)
            // New structured format (Matchweeks)
            data.results.map(mw => `
                            <div style="background-color: #1e293b; padding: 8px 12px; margin-top: 10px; border-radius: 6px; font-weight: bold; color: #94a3b8; font-size: 13px; border-bottom: 1px solid #334155;">
                                ${mw.matchweek}
                            </div>
                            ${mw.dates ?
                    mw.dates.map(dateGroup => `
                                    <div style="background-color: #0f172a; color: #94a3b8; font-size: 12px; padding: 4px 8px; margin-top: 5px; border-left: 2px solid #3b82f6;">
                                        📅 ${dateGroup.date}
                                    </div>
                                    ${dateGroup.matches.map(match => `
                                        <div class="match-result" style="border-bottom: 1px solid #1e293b;">
                                            <div class="team-cell">
                                                <div class="team-logo">${match.home.substring(0, 1)}</div>
                                                <span>${match.home}</span>
                                            </div>
                                            <div class="match-score">${match.score}</div>
                                            <div class="team-cell">
                                                <span>${match.away}</span>
                                                <div class="team-logo">${match.away.substring(0, 1)}</div>
                                            </div>
                                            <div style="font-size: 11px; color: #64748b; margin-left: 10px; width: 100%; display: flex; justify-content: space-between; margin-top: 4px;">
                                                <span>${match.scorers && match.scorers.length > 0 ? '⚽ ' + match.scorers.join(', ') : ''}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                `).join('')
                    :
                    mw.matches.map(match => `
                                <div class="match-result" style="border-bottom: 1px solid #1e293b;">
                                    <div class="team-cell">
                                        <div class="team-logo">${match.home.substring(0, 1)}</div>
                                        <span>${match.home}</span>
                                    </div>
                                    <div class="match-score">${match.score}</div>
                                    <div class="team-cell">
                                        <span>${match.away}</span>
                                        <div class="team-logo">${match.away.substring(0, 1)}</div>
                                    </div>
                                    <div style="font-size: 11px; color: #64748b; margin-left: 10px; width: 100%; display: flex; justify-content: space-between; margin-top: 4px;">
                                        <span>${match.scorers && match.scorers.length > 0 ? '⚽ ' + match.scorers.join(', ') : ''}</span>
                                    </div>
                                </div>
                            `).join('')}
                        `).join('')
            :
            // Legacy/Simple format for other leagues
            data.results.map(match => `
                        <div class="match-result">
                            <div class="team-cell">
                                <div class="team-logo">${match.home.substring(0, 1)}</div>
                                        <span>${match.home}</span>
                                    </div>
                                    <div class="match-score">${match.score}</div>
                                    <div class="team-cell">
                                        <span>${match.away}</span>
                                        <div class="team-logo">${match.away.substring(0, 1)}</div>
                                    </div>
                            <div style="font-size: 11px; color: #64748b; margin-left: 10px;">
                                <div>${match.date}</div>
                                <div>${match.scorers && match.scorers.length ? match.scorers.join(', ') : ''}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="right-col">
                <div class="stats-table-container">
                    <div class="card-header">Estadísticas de Jugadores</div>
                    ${data.players && data.players.length > 0 ? data.players.map(player => `
                        <div class="player-item" onclick="showPlayer(${player.id}, '${league}')">
                            <div class="team-cell">
                                <div class="team-logo" style="background-color: #3b82f6; color: white;">${player.name.substring(0, 1)}</div>
                                <div>
                                    <div style="font-weight: bold; color: #f1f5f9;">${player.name}</div>
                                    <div style="font-size: 12px; color: #94a3b8;">${player.team}</div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-weight: bold; color: #f59e0b;">${player.goals} G</div>
                                <div style="font-size: 12px; color: #94a3b8;">${player.assists} A</div>
                                ${player.injured ? '<div style="font-size: 10px; color: #ef4444;">Lesionado</div>' : ''}
                            </div>
                        </div>
                    `).join('') : '<div style="padding:10px; color:#94a3b8;">No disponible</div>'}
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function showPlayer(id, league) {
    const player = window.leagueData[league].players.find(p => p.id === id);
    if (!player) return;

    const modal = document.getElementById('playerModal');
    const modalBody = document.getElementById('modalBody');

    modalBody.innerHTML = `
        <div class="player-profile-header">
            <div class="player-avatar-large">${player.name.substring(0, 1)}</div>
            <h2 style="margin-bottom: 5px;">${player.name}</h2>
            <div style="color: #94a3b8; margin-bottom: 15px;">${player.team} | ${player.nationality}</div>
            ${player.injured ? '<div style="background-color: #450a0a; color: #fca5a5; padding: 5px; border-radius: 5px; display: inline-block; font-size: 12px;">🚑 Actualmente Lesionado</div>' : ''}
        </div>
        
        <div class="player-stats-grid">
            <div class="stat-box">
                <div class="stat-value">${player.goals}</div>
                <div class="stat-label">Goles</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${player.assists}</div>
                <div class="stat-label">Asistencias</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${player.dob}</div>
                <div class="stat-label">Fecha Nacimiento</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${player.height}</div>
                <div class="stat-label">Altura</div>
            </div>
        </div>

        <div style="margin-top: 20px;">
            <h3 style="font-size: 16px; margin-bottom: 10px; color: #3b82f6;">Historial de Equipos</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${player.history.map(team => `
                    <span style="background-color: #1e293b; padding: 5px 10px; border-radius: 15px; font-size: 12px; border: 1px solid #334155;">${team}</span>
                `).join('')}
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('playerModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('playerModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    // Optionally render the default league, but the section might be hidden.
    // If hidden, this just prepares the content.
    showLeague('premier');
});

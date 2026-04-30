window.leagueData = {};

function showFootballSection() {
    const section = document.getElementById('football-stats-section');
    if (section) {
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

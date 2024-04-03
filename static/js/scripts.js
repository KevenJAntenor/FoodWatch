
document.addEventListener('DOMContentLoaded', (event) => {
    const currentYear = new Date().getFullYear();
    document.querySelector('.footer .text-muted').textContent = `© ${currentYear} Zhao Lin Wu et Keven Jude Antenor. All rights reserved.`;
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quick-search-form');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        fetch(`/contrevenants?du=${startDate}&au=${endDate}`)
            .then(response => response.json())
            .then(data => {
                resultsBody.innerHTML = '';
                data.forEach(violation => {
                    const row = `<tr>
                                    <td>${violation.etablissement}</td>
                                    <td>${violation.count}</td>
                                 </tr>`;
                    resultsBody.innerHTML += row;
                });
                resultsTable.style.display = 'table';
            })
            .catch(error => console.error('Error fetching data:', error));
    });
});

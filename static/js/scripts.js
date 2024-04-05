
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

document.addEventListener('DOMContentLoaded', function() {
    const dropdown = document.getElementById('select-restaurant');

    fetch('/restaurant_names')
        .then(response => response.json())
        .then(names => {
            names.forEach(name => {
                const option = new Option(name, name);
                dropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading restaurant names:', error));
});



document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('recherche-nom-restaurant');
    const resultsDiv = document.getElementById('affichage-infractions'); // Make sure this ID is correct

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const selectedRestaurant = document.getElementById('select-restaurant').value;

        console.log('Fetching infractions for:', selectedRestaurant);

        fetch(`/infractions_par_restaurant?nom=${encodeURIComponent(selectedRestaurant)}`)
            .then(response => response.json())
            .then(infractions => {

                resultsDiv.innerHTML = '';


                 infractions.forEach(infraction => {

                    let dateString = String(infraction.date);

                    if (dateString.length === 8) {
                        const readableDate = `${dateString.substring(0, 4)}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`;

                        const content = `
                            <div class="col-md-4 mb-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">${infraction.etablissement}</h5>
                                        <p class="card-text"><strong>Date:</strong> ${readableDate}</p>
                                        <p class="card-text">${infraction.description}</p>
                                        <p class="card-text"><strong>Adresse:</strong> ${infraction.adresse}</p>
                                        <p class="card-text"><strong>Montant de l'amende:</strong> ${infraction.montant}</p>
                                        <p class="card-text"><strong>Propriétaire:</strong> ${infraction.proprietaire}</p>
                                        <p class="card-text"><strong>Statut:</strong> ${infraction.statut}</p>
                                        <p class="card-text"><strong>Catégorie:</strong> ${infraction.categorie}</p>
                                    </div>
                                </div>
                            </div>
                        `;
                        resultsDiv.innerHTML += content;
                    } else {
                        console.error('Invalid date format:', dateString);
                    }
                });
            })
            .catch(error => console.error('Error fetching restaurant violations:', error));
    });
});

document.addEventListener('DOMContentLoaded', function() {
    $('#submitComplaintButton').click(function(e) {
        e.preventDefault();

        var formData = {
            nom_etablissement: $('#establishment').val(),
            adresse: $('#address').val(),
            ville: $('#city').val(),
            date_visite: $('#visitDate').val(),
            nom_client: $('#lastName').val(),
            prenom_client: $('#firstName').val(),
            description_probleme: $('#description').val()
        };

        if (!formData.nom_etablissement || !formData.adresse || !formData.ville || !formData.date_visite || !formData.nom_client || !formData.prenom_client || !formData.description_probleme) {
            $('#flashMessages').removeClass('d-none').addClass('alert-danger').text('Tous les champs sont requis.').fadeTo(5000, 500).slideUp(500, function() {
                $('#flashMessages').slideUp(500);
            });
            return;
        }

        $.ajax({
            url: '/demande_inspection',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#flashMessages').removeClass('d-none alert-danger').addClass('alert-success').text('La plainte a été soumise avec succès.').fadeTo(5000, 500).slideUp(500, function() {
                    $('#flashMessages').slideUp(500);
                });
                $('#complaintForm')[0].reset();
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors de la soumission de la plainte:', xhr.responseText);
                $('#flashMessages').removeClass('d-none alert-success').addClass('alert-danger').text('Erreur lors de la soumission de la plainte. Veuillez réessayer.').fadeTo(5000, 500).slideUp(500, function() {
                    $('#flashMessages').slideUp(500);
                });
            }
        });
    });
});












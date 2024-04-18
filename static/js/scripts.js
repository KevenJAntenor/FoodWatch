
document.addEventListener('DOMContentLoaded', (event) => {
    const currentYear = new Date().getFullYear();
    document.querySelector('.footer .text-muted').textContent = `© ${currentYear} Zhao Lin Wu et Keven Jude Antenor. All rights reserved.`;
});


document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('quick-search-form');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        fetch(`/contrevenants?du=${startDate}&au=${endDate}`)
            .then(response => response.json())
            .then(data => {
                resultsBody.innerHTML = '';
                data.forEach(violation => {
                    console.log(is_admin_authenticated);
                    const row = `<tr data-id="${violation.id}">
                                    <td contenteditable="false" class="editable etablissement">${violation.etablissement}</td>
                                    <td contenteditable="false">${violation.count}</td>
                                    ${is_admin_authenticated ? `<td>
                                        <button class="btn btn-primary btn-sm edit-btn">Edit</button>
                                        <button class="btn btn-danger btn-sm delete-btn">Delete</button>
                                        <button class="btn btn-success btn-sm save-btn" style="display:none;">Save</button>
                                        <button class="btn btn-warning btn-sm cancel-btn" style="display:none;">Cancel</button>
                                    </td>` : ''}
                                 </tr>`;
                    resultsBody.innerHTML += row;
                });
                resultsTable.style.display = 'table';

                if (is_admin_authenticated) {
                    document.querySelectorAll('.edit-btn').forEach(button => {
                        button.addEventListener('click', function () {
                            const tr = button.closest('tr');
                            tr.dataset.originalEtablissement = tr.querySelector('.etablissement').textContent;

                            tr.querySelectorAll('.editable').forEach(td => {
                                td.contentEditable = true;
                            });
                            tr.querySelector('.save-btn').style.display = '';
                            tr.querySelector('.cancel-btn').style.display = '';
                            button.style.display = 'none';
                        });
                    });

                    document.querySelectorAll('.save-btn').forEach(button => {
                        button.addEventListener('click', function () {
                            const tr = button.closest('tr');
                            const id = tr.dataset.id;
                            const originalEtablissement = tr.dataset.originalEtablissement;
                            const new_etablissement = tr.querySelector('.etablissement').textContent;

                            fetch('/update_establishment/' + originalEtablissement, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ new_etablissement, originalEtablissement })
                            })
                                .then(response => {
                                    if (!response.ok) {
                                        return response.json().then(data => {
                                            alert(data.message);
                                            throw new Error('Server responded with status: ' + response.status);
                                        });
                                    } else {
                                        return response.json().then(data => {
                                            alert(data.message);
                                        });
                                    }
                                })
                                .then(data => {
                                    console.log(data.error);
                                })
                                .catch(error => {
                                    console.error('Error updating data:', error);

                                    tr.querySelector('.etablissement').textContent = tr.dataset.originalEtablissement;
                                });

                            tr.querySelectorAll('.editable').forEach(td => {
                                td.contentEditable = false;
                            });
                            tr.querySelector('.edit-btn').style.display = '';
                            button.style.display = 'none';
                            tr.querySelector('.cancel-btn').style.display = 'none';
                        });

                    });

                    document.querySelectorAll('.cancel-btn').forEach(button => {
                        button.addEventListener('click', function () {
                            const tr = button.closest('tr');
                            tr.querySelector('.etablissement').textContent = tr.dataset.originalEtablissement;

                            tr.querySelectorAll('.editable').forEach(td => {
                                td.contentEditable = false;
                            });
                            tr.querySelector('.edit-btn').style.display = '';
                            tr.querySelector('.save-btn').style.display = 'none';
                            button.style.display = 'none';
                        });
                    });

                    document.querySelectorAll('.delete-btn').forEach(button => {
                        button.addEventListener('click', function () {
                            const tr = button.closest('tr');
                            const id = tr.dataset.id;
                            const etablissement = tr.querySelector('.etablissement').textContent;

                            fetch('/delete_establishment/' + etablissement, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ etablissement })
                            })
                                .then(response => {
                                    if (!response.ok) {
                                        return response.json().then(data => {
                                            alert(data.message);
                                            throw new Error('Server responded with status: ' + response.status);
                                        });
                                    } else {
                                        return response.json().then(data => {
                                            alert(data.message);
                                            tr.remove(); // Remove the row from the table

                                        });
                                    }
                                })
                                .then(data => {
                                    console.log(data.message);
                                })
                                .catch(error => console.error('Error deleting data:', error));
                        });
                    });
                }
            })
            .catch(error => console.error('Error fetching data:', error));
    });
});

document.addEventListener('DOMContentLoaded', function () {
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



document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.getElementById('recherche-nom-restaurant');
    const resultsDiv = document.getElementById('affichage-infractions');

    searchForm.addEventListener('submit', function (e) {
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

document.addEventListener('DOMContentLoaded', function () {
    $('#submitComplaintButton').click(function (e) {
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
            $('#flashMessages').removeClass('d-none').addClass('alert-danger').text('Tous les champs sont requis.').fadeTo(5000, 500).slideUp(500, function () {
                $('#flashMessages').slideUp(500);
            });
            return;
        }

        $.ajax({
            url: '/demande_inspection',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                $('#flashMessages').removeClass('d-none alert-danger').addClass('alert-success').text('La plainte a été soumise avec succès.').fadeTo(5000, 500).slideUp(500, function () {
                    $('#flashMessages').slideUp(500);
                });
                $('#complaintForm')[0].reset();
            },
            error: function (xhr, status, error) {
                console.error('Erreur lors de la soumission de la plainte:', xhr.responseText);
                $('#flashMessages').removeClass('d-none alert-success').addClass('alert-danger').text('Erreur lors de la soumission de la plainte. Veuillez réessayer.').fadeTo(5000, 500).slideUp(500, function () {
                    $('#flashMessages').slideUp(500);
                });
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formulaire');
    const nom = document.getElementById('nom');
    const courriel = document.getElementById('courriel');
    const selectEstablishments = document.getElementById('select-establishments');
    const mdp = document.getElementById('mdp');
    const mdpConf = document.getElementById('mdpConf');

    form.addEventListener('submit', function (event) {
        let isValid = true;

        document.getElementById('errNom').textContent = '';
        document.getElementById('errCourriel').textContent = '';
        document.getElementById('errSelect').textContent = '';
        document.getElementById('errMdp').textContent = '';
        document.getElementById('errMdpConf').textContent = '';

        if (nom.value.trim() === '') {
            document.getElementById('errNom').textContent = 'Veuillez entrer votre nom complet.';
            isValid = false;
        }

        if (courriel.value.trim() === '') {
            document.getElementById('errCourriel').textContent = 'Veuillez entrer votre courriel.';
            isValid = false;
        } else if (!isValidEmail(courriel.value.trim())) {
            document.getElementById('errCourriel').textContent = 'Veuillez entrer une adresse courriel valide.';
            isValid = false;
        }

        if (selectEstablishments.selectedOptions.length === 0) {
            document.getElementById('errSelect').textContent = 'Veuillez choisir au moins un établissement.';
            isValid = false;
        }

        if (mdp.value.trim() === '') {
            document.getElementById('errMdp').textContent = 'Veuillez entrer votre mot de passe.';
            isValid = false;
        } else if (mdp.value.trim().length < 8 || !/\d/.test(mdp.value.trim())) {
            document.getElementById('errMdp').textContent = 'Le mot de passe doit contenir au moins 8 caractères avec au moins 1 chiffre.';
            isValid = false;
        }

        if (mdpConf.value.trim() === '') {
            document.getElementById('errMdpConf').textContent = 'Veuillez confirmer votre mot de passe.';
            isValid = false;
        } else if (mdpConf.value.trim() !== mdp.value.trim()) {
            document.getElementById('errMdpConf').textContent = 'Les mots de passe ne correspondent pas.';
            isValid = false;
        }

        if (isValid) {
            const selectEstablishments = document.getElementById('select-establishments');
            const selectedOptions = Array.from(selectEstablishments.selectedOptions).map(option => option.value);

            const establishmentsInput = document.createElement('input');
            establishmentsInput.type = 'hidden';
            establishmentsInput.name = 'selectedEstablishments';
            establishmentsInput.value = JSON.stringify(selectedOptions);
            form.appendChild(establishmentsInput);
        } else {
            event.preventDefault();
        }
    });

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const establishmentsSelect = document.getElementById('select-establishments');

    fetch('/establishments')
        .then(response => response.json())
        .then(data => {
            data.forEach(establishment => {
                const option = document.createElement('option');
                option.value = establishment.etablissement;
                option.textContent = establishment.etablissement + " - Infractions: " + establishment.infraction_count;
                establishmentsSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Erreur lors du chargement des établissements:', error));

    const resultsDiv = document.getElementById('affichage-infractions');


});

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', function (event) {
        let formIsValid = true;

        document.querySelectorAll('.invalid-feedback').forEach(function (element) {
            element.style.display = 'none';
        });

        if (!emailInput.value.trim()) {
            displayErrorMessage(emailInput, 'Please enter your email.');
            formIsValid = false;
        } else if (!isValidEmail(emailInput.value.trim())) {
            displayErrorMessage(emailInput, 'Please enter a valid email address.');
            formIsValid = false;
        }

        if (!passwordInput.value.trim()) {
            displayErrorMessage(passwordInput, 'Please enter your password.');
            formIsValid = false;
        }

        if (!formIsValid) {
            event.preventDefault();
        }

        function displayErrorMessage(inputElement, message) {
            const feedbackElement = inputElement.nextElementSibling;
            feedbackElement.textContent = message;
            feedbackElement.style.display = 'block';
        }

        function isValidEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('profilePic');
    const form = document.getElementById('profile-pic-form');
    const errorDisplay = document.createElement('p');
    errorDisplay.className = 'text-danger';
    fileInput.parentNode.insertBefore(errorDisplay, fileInput.nextSibling);

    form.addEventListener('submit', function (event) {
        const file = fileInput.files[0];
        if (file) {
            const fileName = file.name.toLowerCase();
            const validExtensions = ['.jpg', '.jpeg', '.png'];
            const maxFileSize = 100 * 1024;
            console.log("size :", file.size)

            if (!validExtensions.some(ext => fileName.endsWith(ext))) {
                errorDisplay.textContent = 'Seuls les fichiers .jpg, .jpeg ou .png sont autorisés.';
                event.preventDefault();
            } else if (file.size > maxFileSize) {
                errorDisplay.textContent = 'Le fichier est trop volumineux. La taille maximale autorisée est de 100KB.';
                event.preventDefault();
            } else {
                errorDisplay.textContent = '';
            }
        } else {
            errorDisplay.textContent = 'Veuillez sélectionner un fichier à téléverser.';
            event.preventDefault();
        }
    });
});
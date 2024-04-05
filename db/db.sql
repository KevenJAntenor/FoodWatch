CREATE TABLE IF NOT EXISTS violations (
    id_poursuite INTEGER,
    business_id INTEGER,
    date INTEGER,
    description TEXT,
    adresse TEXT,
    date_jugement INTEGER,
    etablissement TEXT,
    montant INTEGER,
    proprietaire TEXT,
    ville TEXT,
    statut TEXT,
    date_statut INTEGER,
    categorie TEXT,
    PRIMARY KEY(id_poursuite)
);

CREATE TABLE IF NOT EXISTS inspection_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_etablissement TEXT NOT NULL,
    adresse TEXT NOT NULL,
    ville TEXT NOT NULL,
    date_visite TEXT NOT NULL,
    nom_client TEXT NOT NULL,
    prenom_client TEXT NOT NULL,
    description_probleme TEXT NOT NULL
);



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

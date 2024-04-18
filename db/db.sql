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

CREATE TABLE IF NOT EXISTS utilisateurs (
    utilisateur_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_complet VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    token VARCHAR(255),
    photo_profil BLOB,
    role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user'))
);


CREATE TABLE IF NOT EXISTS utilisateurs_etablissements (
    utilisateur_id INT,
    nom_etablissement TEXT NOT NULL,
    PRIMARY KEY (utilisateur_id, nom_etablissement),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(utilisateur_id),
    FOREIGN KEY (nom_etablissement) REFERENCES violations(etablissement)
);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_session VARCHAR(100),
  email VARCHAR(255) UNIQUE NOT NULL
);


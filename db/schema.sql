CREATE TABLE IF NOT EXISTS pays (
    "Id_pays"           SERIAL PRIMARY KEY,
    nom                 VARCHAR(50),
    temp_tolerance      NUMERIC(15, 2),
    humidity_tolerance  NUMERIC(15, 2),
    temp_min            NUMERIC(15, 2),
    temp_max            NUMERIC(15, 2),
    humidity_min        NUMERIC(15, 2),
    humidity_max        NUMERIC(15, 2)
);

CREATE TABLE IF NOT EXISTS exploitation (
    "Id_exploitation"   SERIAL PRIMARY KEY,
    ville               VARCHAR(50),
    adresse             VARCHAR(50),
    nom_exploitation    VARCHAR(50),
    "Id_pays"           INTEGER REFERENCES pays("Id_pays")
);

CREATE TABLE IF NOT EXISTS entrepot (
    "Id_entrepot"       SERIAL PRIMARY KEY,
    localisation        VARCHAR(50),
    nom                 VARCHAR(50),
    capacite_stockage   INTEGER,
    "Id_exploitation"   INTEGER REFERENCES exploitation("Id_exploitation")
);

CREATE TABLE IF NOT EXISTS lot (
    "Id_lot"            SERIAL PRIMARY KEY,
    date_stockage       DATE,
    statut              VARCHAR(50) DEFAULT 'conforme',
    quantite            INTEGER,
    date_expiration     DATE,
    "Id_entrepot"       INTEGER REFERENCES entrepot("Id_entrepot")
);

CREATE TABLE IF NOT EXISTS mesure (
    "Id_measure"        SERIAL PRIMARY KEY,
    temperature         NUMERIC(15, 2),
    humidite            NUMERIC(15, 2),
    date_mesure         TIMESTAMP,
    "Id_entrepot"       INTEGER REFERENCES entrepot("Id_entrepot")
);

CREATE TABLE IF NOT EXISTS alert (
    "Id_alert"          SERIAL PRIMARY KEY,
    message             VARCHAR(200),
    type_alerte         VARCHAR(50),
    niveau              VARCHAR(50),
    created_at          TIMESTAMP,
    "Id_lot"            INTEGER REFERENCES lot("Id_lot")
);

-- Index utile pour la requête FIFO
CREATE INDEX IF NOT EXISTS idx_lot_date_stockage ON lot(date_stockage);

-- =====================================================================
-- Données de démonstration (Brésil)
-- =====================================================================
INSERT INTO pays (nom, temp_tolerance, humidity_tolerance, temp_min, temp_max, humidity_min, humidity_max)
SELECT 'Brazil', 3.0, 2.0, 26.0, 32.0, 53.0, 57.0
WHERE NOT EXISTS (SELECT 1 FROM pays WHERE nom = 'Brazil');

-- Pays prêts pour l'extension (à décommenter le moment venu) :
-- Équateur : 31°C ±3 / 60% ±2  -> 28-34 / 58-62
-- Colombie : 26°C ±3 / 80% ±2  -> 23-29 / 78-82

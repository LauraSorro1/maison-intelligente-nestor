-- Schéma MariaDB — Projet 1: Station de surveillance d'objets connectés
--
-- Le projet exige UNE table par capteur. Chaque table contient au minimum :
--   - un horodatage
--   - une valeur
--   - une unité
--
-- Charger avec :  mariadb -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS station_iot
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE station_iot;

-- Capteur de température de l'aquarium (salon) — SEUL CAPTEUR D'EXEMPLE.
-- Le nom de la table doit correspondre à l'entrée de config.TABLES_CAPTEURS.
-- Pour chaque nouveau capteur, ajoutez une table sur ce modèle ET une
-- entrée correspondante dans config.TABLES_CAPTEURS.
CREATE TABLE IF NOT EXISTS lectures_temperature_aquarium (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    horodatage  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    valeur      VARCHAR(80) NOT NULL,
    unite       VARCHAR(16) NOT NULL,
    INDEX idx_horodatage (horodatage)
) ENGINE=InnoDB;

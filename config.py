"""Configuration partagée du Projet : de simples constantes.

Toute la configuration (courtier MQTT, base de données, sujets MQTT) est
centralisée ici afin que les capteurs, les actionneurs et le contrôleur
parlent tous le même langage.

Le mot de passe de la base est lu dans le fichier .env (non versionné) :
voir .env.exemple pour le modèle à copier.
"""

import os
from enum import StrEnum

from dotenv import load_dotenv

load_dotenv()

# --- Courtier MQTT (Mosquitto) ---
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# --- Base de données MariaDB ---
# Ajustés selon mon installation locale.
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "maison"
DB_PORT = 3306

if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD absent : copier .env.exemple en .env")

# --- Sujets MQTT des capteurs (publieurs) ---
class SujetsCapteurs(StrEnum):
    # Salon
    SALON_TEMPERATURE           = "maison/salon/temperature"
    SALON_LUMINOSITE            = "maison/salon/luminosite"
    SALON_HUMIDITE              = "maison/salon/humidite"
    # Aquarium (salon)
    SALON_AQUARIUM_TEMPERATURE  = "maison/salon/aquarium/temperature"
    SALON_AQUARIUM_PH           = "maison/salon/aquarium/ph"
    SALON_AQUARIUM_NIVEAU       = "maison/salon/aquarium/niveau"
    # Entrée
    ENTREE_MOUVEMENT            = "maison/entree/mouvement"
    ENTREE_PORTE                = "maison/entree/porte"
    # Garage
    GARAGE_TEMPERATURE          = "maison/garage/temperature"
    GARAGE_CO                   = "maison/garage/co"
    GARAGE_VEHICULE             = "maison/garage/vehicule"
    GARAGE_BARCODE              = "maison/garage/barcode"

# --- Sujets MQTT des actionneurs (abonnés) ---
class SujetsActionneurs(StrEnum):
    # Salon
    SALON_LUMIERE_CMD           = "maison/salon/lumiere/cmd"
    SALON_LUMIERE_ETAT          = "maison/salon/lumiere/etat"
    SALON_THERMOPOMPE_CMD       = "maison/salon/thermopompe/cmd"
    SALON_THERMOPOMPE_ETAT      = "maison/salon/thermopompe/etat"
    # Aquarium (salon)
    SALON_AQUARIUM_POMPE_CMD    = "maison/salon/aquarium/pompe/cmd"
    SALON_AQUARIUM_POMPE_ETAT   = "maison/salon/aquarium/pompe/etat"
    SALON_AQUARIUM_UV_CMD       = "maison/salon/aquarium/uv/cmd"
    SALON_AQUARIUM_UV_ETAT      = "maison/salon/aquarium/uv/etat"
    # Entrée
    ENTREE_SERRURE_CMD          = "maison/entree/serrure/cmd"
    ENTREE_SERRURE_ETAT         = "maison/entree/serrure/etat"
    ENTREE_LUMIERE_CMD          = "maison/entree/lumiere/cmd"
    ENTREE_LUMIERE_ETAT         = "maison/entree/lumiere/etat"
    # Garage
    GARAGE_CHAUFFAGE_CMD        = "maison/garage/chauffage/cmd"
    GARAGE_CHAUFFAGE_ETAT       = "maison/garage/chauffage/etat"
    GARAGE_PORTE_CMD            = "maison/garage/porte/cmd"
    GARAGE_PORTE_ETAT           = "maison/garage/porte/etat"
    GARAGE_LUMIERE_CMD          = "maison/garage/lumiere/cmd"
    GARAGE_LUMIERE_ETAT         = "maison/garage/lumiere/etat"

# --- Sujet MQTT du journal vocal (Projet 2) ---
# L'assistant y publie chaque interaction pour affichage dans Node-RED.
SUJET_JOURNAL_VOCAL = "assistant/journal"

# --- Correspondance type de capteur → table SQL (Projet 2) ---
TABLES_CAPTEURS = {
    # Salon
    "temperature_salon":        "lectures_temperature_salon",
    "luminosite_salon":         "lectures_luminosite_salon",
    "humidite_salon":           "lectures_humidite_salon",
    # Aquarium
    "temperature_aquarium":     "lectures_temperature_aquarium",
    "ph_aquarium":              "lectures_ph_aquarium",
    "niveau_aquarium":          "lectures_niveau_aquarium",
    # Entrée
    "mouvement_entree":         "lectures_mouvement_entree",
    "porte_entree":             "lectures_porte_entree",
    # Garage
    "temperature_garage":       "lectures_temperature_garage",
    "co_garage":                "lectures_co_garage",
    "vehicule_garage":          "lectures_vehicule_garage",
    "barcode_garage":           "lectures_barcode_garage",
}



"""Configuration partagée du Projet : de simples constantes.

Toute la configuration (courtier MQTT, base de données, sujets MQTT) est
centralisée ici afin que les capteurs, les actionneurs et le contrôleur
parlent tous le même langage.
"""

from enum import StrEnum

# --- Courtier MQTT (Mosquitto) ---
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# --- Sujets MQTT des capteurs (publieurs) ---
# Un capteur publie sous maison/.../<grandeur> : commencez toujours par
# maison/ et finissez par la grandeur mesurée. Le nombre de niveaux
# intermédiaires est libre, du moment qu'il reste cohérent.
# Ajoutez vos propres sujets à l'enum quand vous créez de nouveaux capteurs.

class SujetsCapteurs(StrEnum):
# Mes capteurs
    SALON_TEMPERATURE = "maison/salon/temperature"
    SALON_LUMINOSITE = "maison/salon/luminosite"
    CHAMBRE_TEMPERATURE = "maison/chambre/temperature"
    CHAMBRE_HUMIDITE = "maison/chambre/humidite"
    ENTREE_MOUVEMENT = "maison/entree/mouvement"
    ENTREE_PORTE = "maison/entree/porte"
    GARAGE_TEMPERATURE = "maison/garage/temperature"
    GARAGE_VEHICULE = "maison/garage/vehicule"
# Capteurs de la prof :
    SALON_AQUARIUM = "maison/salon/aquarium/temperature"
    SALON_AQUARIUM_PH = "maison/salon/aquarium/ph"

# --- Sujets MQTT des actionneurs (abonnés) ---
# /cmd : le contrôleur publie une commande ; l'actionneur y est abonné.
# /etat : l'actionneur publie son état courant (utile au tableau de bord).

class SujetsActionneurs(StrEnum):
    SALON_LUMIERE_CMD = "maison/salon/lumiere/cmd"
    SALON_LUMIERE_ETAT = "maison/salon/lumiere/etat"
    SALON_THERMOPOMPE_CMD = "maison/salon/thermopompe/cmd"
    SALON_THERMOPOMPE_ETAT = "maison/salon/thermopompe/etat"
    CHAMBRE_THERMOPOMPE_CMD = "maison/chambre/thermopompe/cmd"
    CHAMBRE_THERMOPOMPE_ETAT = "maison/chambre/thermopompe/etat"
    ENTREE_SERRURE_CMD = "maison/entree/serrure/cmd"
    ENTREE_SERRURE_ETAT = "maison/entree/serrure/etat"
    ENTREE_LUMIERE_CMD = "maison/entree/lumiere/cmd"
    ENTREE_LUMIERE_ETAT = "maison/entree/lumiere/etat"
    GARAGE_CHAUFFAGE_CMD = "maison/garage/chauffage/cmd"
    GARAGE_CHAUFFAGE_ETAT = "maison/garage/chauffage/etat"
    GARAGE_PORTE_CMD = "maison/garage/porte/cmd"
    GARAGE_PORTE_ETAT = "maison/garage/porte/etat"

# --- Correspondance type de capteur → table SQL ---
# db.py traduit type_capteur en nom de table via ce dictionnaire ;
# un type inconnu lève une erreur claire plutôt qu'une requête invalide.
# Ajoutez une entrée par capteur.

TABLES_CAPTEURS = {
    "temperature_salon": "lectures_temperature_salon",
    "luminosite_salon": "lectures_luminosite_salon",
    "temperature_aquarium": "lectures_temperature_aquarium",
    "ph_aquarium": "lectures_ph_aquarium",
    "temperature_chambre": "lectures_temperature_chambre",
    "humidite_chambre": "lectures_humidite_chambre",
    "mouvement_entree": "lectures_mouvement_entree",
    "porte_entree": "lectures_porte_entree",
    "temperature_garage": "lectures_temperature_garage",
    "vehicule_garage": "lectures_vehicule_garage",
}

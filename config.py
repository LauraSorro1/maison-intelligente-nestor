"""Configuration partagée du Projet : de simples constantes.

Toute la configuration (courtier MQTT, base de données, sujets MQTT) est
centralisée ici afin que les capteurs, les actionneurs et le contrôleur
parlent tous le même langage.
"""

from enum import StrEnum

# --- Courtier MQTT (Mosquitto) ---
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# --- Base de données MariaDB ---
# Ajustez l'utilisateur et le mot de passe selon votre installation locale.
DB_HOST = "127.0.0.1"  
DB_USER = "utilisateur"
DB_PASSWORD = "motdepasse"
DB_NAME = "maison"

# --- Sujets MQTT des capteurs (publieurs) ---
# Un capteur publie sous maison/.../<grandeur> : commencez toujours par
# maison/ et finissez par la grandeur mesurée. Le nombre de niveaux
# intermédiaires est libre, du moment qu'il reste cohérent.
# Ajoutez vos propres sujets à l'enum quand vous créez de nouveaux capteurs.

class SujetsCapteurs(StrEnum):
    SALON_AQUARIUM = "maison/salon/aquarium/temperature"
    SALON_AQUARIUM_PH = "maison/salon/aquarium/ph"

# --- Sujets MQTT des actionneurs (abonnés) ---
# /cmd : le contrôleur publie une commande ; l'actionneur y est abonné.
# /etat : l'actionneur publie son état courant (utile au tableau de bord).

class SujetsActionneurs(StrEnum):
    AQUARIUM_CMD = "maison/salon/aquarium/cmd"
    AQUARIUM_ETAT = "maison/salon/aquarium/etat"

# --- Correspondance type de capteur → table SQL ---
# db.py traduit type_capteur en nom de table via ce dictionnaire ;
# un type inconnu lève une erreur claire plutôt qu'une requête invalide.
# Ajoutez une entrée par capteur.

TABLES_CAPTEURS = {
    "temperature_aquarium": "lectures_temperature_aquarium",
}

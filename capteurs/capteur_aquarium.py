"""Capteur de température de l'aquarium — classe Python.

Publie une valeur en degrés Celsius sur maison/salon/aquarium/temperature.
CECI EST UN EXEMPLE DE CAPTEUR : créez vos propres capteurs pour les
autres grandeurs.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_aquarium
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurAquarium(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="temperature_aquarium",
            sujet=SujetsCapteurs.SALON_AQUARIUM,
            unite="C",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="capteur-aquarium")
        )
        self.valeur = 21.0  # température de départ

    def lire(self):
        # NOTE: Ceci est un exemple d'implementation.
        # Les capteurs que vous allez simuler ne produiront pas de valeurs aléatoires.
        self.valeur = random.uniform(0, 100)
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurAquarium().demarrer()

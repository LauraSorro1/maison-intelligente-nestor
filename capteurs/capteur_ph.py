"""Capteur de pH de l'aquarium — classe Python.

Publie une valeur de pH sur maison/salon/aquarium/ph.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_ph
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurPh(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="ph_aquarium",
            sujet=SujetsCapteurs.SALON_AQUARIUM_PH,
            unite="pH",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="capteur-ph")
        )
        self.valeur = 7.0  # pH de départ

    def lire(self):
        self.valeur = random.uniform(6.5, 8.5)
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurPh().demarrer()

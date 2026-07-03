"""Capteur de luminosité du salon — classe Python.

Publie une valeur en lux sur maison/salon/luminosite.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_salon_luminosite
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurSalonLuminosite(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="luminosite_salon",
            sujet=SujetsCapteurs.SALON_LUMINOSITE,
            unite="lux",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="capteur-salon-luminosite")
        )
        self.valeur = 300.0  # valeur de départ - jour

    def lire(self):
        self.valeur += random.uniform(-50.0, 50.0)
        self.valeur = max(0.0, min(1000.0, self.valeur))  # limite la luminosité entre 0 et 1000 lux
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurSalonLuminosite().demarrer()

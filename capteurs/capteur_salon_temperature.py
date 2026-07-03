"""Capteur de température du salon — classe Python.

Publie une valeur en degrés Celsius sur maison/salon/temperature.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_salon_temperature
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurSalonTemperature(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="temperature_salon",
            sujet=SujetsCapteurs.SALON_TEMPERATURE,
            unite="C",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="capteur-salon-temperature")
        )
        self.valeur = 21.0  # température de départ

    def lire(self):
        self.valeur += random.uniform(-0.5, 0.5)
        self.valeur = max(18.0, min(26.0, self.valeur))  # limite la température entre 18 et 26 °C
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurSalonTemperature().demarrer()

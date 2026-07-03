"""Capteur du véhicule dans le garage — classe Python.

Publie l'état du véhicule (présent/absent) sur maison/garage/vehicule.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_garage_vehicule
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurGarageVehicule(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="vehicule_garage",
            sujet=SujetsCapteurs.GARAGE_VEHICULE,
            unite="",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="capteur-garage-vehicule")
        )
        self.valeur = 0  # pas de véhicule au départ

    def lire(self):
        if random.random() < 0.15:
            self.valeur = 1 if self.valeur == 0 else 0
        return self.valeur


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurGarageVehicule().demarrer()

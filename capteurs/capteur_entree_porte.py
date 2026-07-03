"""Capteur de la porte d'entrée — classe Python.

Publie l'état de la porte (ouvert/ferme) sur maison/entree/porte.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_entree_porte
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurEntreePorte(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="porte_entree",
            sujet=SujetsCapteurs.ENTREE_PORTE,
            unite="",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="capteur-entree-porte")
        )
        self.valeur = "ferme"  # porte fermée au départ

    def lire(self):
        if random.random() < 0.1:
            self.valeur = "ouvert" if self.valeur == "ferme" else "ferme"
        return self.valeur


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurEntreePorte().demarrer()

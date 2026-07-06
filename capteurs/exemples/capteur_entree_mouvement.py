"""Capteur de mouvement de l'entrée — classe Python.

Publie une valeur binaire (0 ou 1) sur maison/entrée/mouvement.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_entree_mouvement
"""
import random

import paho.mqtt.client as mqtt

from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurEntreeMouvement(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="mouvement_entree",
            sujet=SujetsCapteurs.ENTREE_MOUVEMENT,
            unite="",
            periode=2.0,
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="capteur-entree-mouvement")
        )
        self.valeur = 0  # pas de mouvement au départ

    def lire(self):
        self.valeur = 1 if random.random() < 0.2 else 0
        return self.valeur


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurEntreeMouvement().demarrer()

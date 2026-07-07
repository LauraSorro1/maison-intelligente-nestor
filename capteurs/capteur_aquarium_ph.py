"""Capteur de pH de l'aquarium — classe Python.

Publie une valeur de pH sur maison/salon/aquarium/ph.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_aquarium_ph
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurAquariumPh(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="ph_aquarium",
            sujet=SujetsCapteurs.SALON_AQUARIUM_PH,
            unite="pH",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-aquarium-ph",
                "maison/salon/aquarium/ph/sante"
            )
        )
        self.valeur = 7.0  # pH de départ

    def lire(self):
        self.valeur += random.uniform(-0.05, 0.05)  # variation très douce
        self.valeur = max(6.8, min(7.5, self.valeur))  # plage normale eau douce
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurAquariumPh().demarrer()

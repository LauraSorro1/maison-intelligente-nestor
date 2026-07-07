"""Capteur du niveau d'eau de l'aquarium — classe Python.

Publie une valeur de niveau sur maison/salon/aquarium/niveau.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_aquarium_niveau
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurAquariumNiveau(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="niveau_aquarium",
            sujet=SujetsCapteurs.SALON_AQUARIUM_NIVEAU,
            unite="%",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-aquarium-niveau",
                "maison/salon/aquarium/niveau/sante"
            )
        )
        self.valeur = 85.0  # niveau de départ, presque plein

    def lire(self):
        self.valeur += random.uniform(-0.2, 0.1)  # variation asymétrique, plus de chance de baisser que de monter (évaporation naturelle) 
        self.valeur = max(60.0, min(100.0, self.valeur))  # plage normale eau douce
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurAquariumNiveau().demarrer()

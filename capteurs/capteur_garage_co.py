"""Capteur du CO du garage — classe Python.

Publie une valeur de CO sur maison/garage/co.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_garage_co
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurGarageCo(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="co_garage",
            sujet=SujetsCapteurs.GARAGE_CO,
            unite="ppm",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-garage-co",
                "maison/garage/co/sante"
            )
        )
        self.valeur = 2.0  # niveau normal sans voiture

    def lire(self):
        self.valeur += random.uniform(-1.0, 1.5)  # variation asymétrique, le CO monte plus vite qu'il ne descend (accumulation dans espace fermé). 
        # Le seuil d'alerte selon Santé Canada est 25 ppm — on le déclenchera dans le contrôleur.
        self.valeur = max(0, min(50.0, self.valeur))  # plage normale
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurGarageCo().demarrer()

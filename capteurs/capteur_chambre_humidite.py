"""Capteur d'humidité de la chambre — classe Python.

Publie une valeur en pourcentage sur maison/chambre/humidite.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_chambre_humidite
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurChambreHumidite(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="humidite_chambre",
            sujet=SujetsCapteurs.CHAMBRE_HUMIDITE,
            unite="%",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-chambre-humidite",
                "maison/chambre/humidite/sante"
            )
        )
        self.valeur = 45.0  # humidité confortable de départ

    def lire(self):
        self.valeur += random.uniform(-2.0, 2.0)
        self.valeur = max(35.0, min(60.0, self.valeur))  # limite l'humidité entre 35% et 60%
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurChambreHumidite().demarrer()

"""Capteur d'humidité du salon — classe Python.

Publie une valeur en pourcentage sur maison/salon/humidite.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_salon_humidite
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurSalonHumidite(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="humidite_salon",
            sujet=SujetsCapteurs.SALON_HUMIDITE,
            unite="%",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-salon-humidite",
                "maison/salon/humidite/sante"
            )
        )
        self.valeur = 45.0  # humidité confortable de départ

    def lire(self):
        self.valeur += random.uniform(-2.0, 2.0)
        self.valeur = max(30.0, min(65.0, self.valeur))  # limite l'humidité entre 30% et 65%
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurSalonHumidite().demarrer()

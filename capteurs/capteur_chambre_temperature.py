"""Capteur de température de la chambre — classe Python.

Publie une valeur en degrés Celsius sur maison/chambre/temperature.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_chambre_temperature
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurChambreTemperature(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="temperature_chambre",
            sujet=SujetsCapteurs.CHAMBRE_TEMPERATURE,
            unite="C",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-chambre-temperature",
                "maison/chambre/temperature/sante"
            )
        )
        self.valeur = 19.0  # légèrement plus frais que le salon

    def lire(self):
        self.valeur += random.uniform(-0.5, 0.5)
        self.valeur = max(16.0, min(24.0, self.valeur))  # limite la température entre 16 et 24 °C
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurChambreTemperature().demarrer()

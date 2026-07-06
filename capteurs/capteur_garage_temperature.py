"""Capteur de température du garage — classe Python.

Publie une valeur en degrés Celsius sur maison/garage/temperature.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_garage_temperature
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurGarageTemperature(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="temperature_garage",
            sujet=SujetsCapteurs.GARAGE_TEMPERATURE,
            unite="C",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-garage-temperature",
                "maison/garage/temperature/sante"
            )
        )
        self.valeur = 4.0  # proche du seuil de déclenchement du chauffage

    def lire(self):
        self.valeur += random.uniform(-0.5, 0.5)
        self.valeur = max(-10.0, min(20.0, self.valeur))  # limite la température entre -10 et 20 °C
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurGarageTemperature().demarrer()

"""Capteur de température de l'aquarium — classe Python.

Publie une valeur en degrés Celsius sur maison/salon/aquarium/temperature.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_aquarium_temperature
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurAquariumTemperature(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="temperature_aquarium",
            sujet=SujetsCapteurs.SALON_AQUARIUM,
            unite="C",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-aquarium-temperature",
                "maison/salon/aquarium/temperature/sante"
            )
        )
        self.valeur = 24.0  # température de départ

    def lire(self):
        self.valeur += random.uniform(-0.3, 0.3) # plus stable qu'une pièce
        self.valeur = max(18.0, min(26.0, self.valeur))  # limite la température entre 18°C et 26°C
        return round(self.valeur, 2)


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurAquariumTemperature().demarrer()

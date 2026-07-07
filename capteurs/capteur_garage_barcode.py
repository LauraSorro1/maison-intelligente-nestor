"""Capteur du barcode du garage — classe Python.

Publie une valeur de code-barres sur maison/garage/barcode.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_garage_barcode
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurGarageBarcode(Capteur):

    CODES_AUTORISES = ["AUTO-001", "AUTO-002", "AUTO-003"]

    def __init__(self):
        super().__init__(
            type_capteur="barcode_garage",
            sujet=SujetsCapteurs.GARAGE_BARCODE,
            unite="",
            periode=2.0,
            client=Capteur.creer_client(
                "capteur-garage-barcode",
                "maison/garage/barcode/sante"
            )
        )
        self.valeur = "INCONNU"  # valeur de départ

    def lire(self):
        # Simule une lecture : 70% de chance d'un code autorisé
        if random.random() < 0.7:
            return random.choice(CapteurGarageBarcode.CODES_AUTORISES)
        else:
            return "INCONNU"


# En lançant ce script, on instancie un capteur et on le démarre :
# il publie des valeurs sur le sujet MQTT à intervalle régulier.
if __name__ == "__main__":
    CapteurGarageBarcode().demarrer()
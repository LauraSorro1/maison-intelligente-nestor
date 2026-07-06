"""Actionneur de la porte du garage — classe Python.

S'abonne à maison/garage/porte/cmd et réagit aux commandes
"ouvre"/"ferme". Publie son état sur maison/garage/porte/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_garage_porte
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurGaragePorte(Actionneur):
    def __init__(self):
        super().__init__(
            nom="garage-porte",
            sujet_cmd=config.SujetsActionneurs.GARAGE_PORTE_CMD,
            sujet_etat=config.SujetsActionneurs.GARAGE_PORTE_ETAT,
            etat_initial="ferme",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-garage-porte")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("ouvre", "open", "1"):
            print("[garage-porte] 🚗 Porte du garage ouverte")
            return "ouvre"
        if commande in ("ferme", "close", "0"):
            print("[garage-porte] 🚪 Porte du garage fermée")
            return "ferme"
        return self.etat


if __name__ == "__main__":
    ActionneurGaragePorte().demarrer()

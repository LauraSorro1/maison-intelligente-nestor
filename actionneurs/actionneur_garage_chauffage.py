"""Actionneur du chauffage du garage — classe Python.

S'abonne à maison/garage/chauffage/cmd et réagit aux commandes
"allume"/"eteint". Publie son état sur maison/garage/chauffage/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_garage_chauffage
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurGarageChauffage(Actionneur):
    def __init__(self):
        super().__init__(
            nom="garage-chauffage",
            sujet_cmd=config.SujetsActionneurs.GARAGE_CHAUFFAGE_CMD,
            sujet_etat=config.SujetsActionneurs.GARAGE_CHAUFFAGE_ETAT,
            etat_initial="eteint",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-garage-chauffage")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("allume", "on", "1"):
            print("[garage-chauffage] 🔥 Chauffage allumé")
            return "allume"
        if commande in ("eteint", "off", "0"):
            print("[garage-chauffage] ⏹️ Chauffage éteint")
            return "eteint"
        return self.etat


if __name__ == "__main__":
    ActionneurGarageChauffage().demarrer()

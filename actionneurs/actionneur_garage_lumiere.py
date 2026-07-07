"""Actionneur de la lumière du garage — classe Python.

S'abonne à maison/garage/lumiere/cmd et réagit aux commandes
"allume"/"eteint". Publie son état sur maison/garage/lumiere/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_garage_lumiere
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurGarageLumiere(Actionneur):
    def __init__(self):
        super().__init__(
            nom="garage-lumiere",
            sujet_cmd=config.SujetsActionneurs.GARAGE_LUMIERE_CMD,
            sujet_etat=config.SujetsActionneurs.GARAGE_LUMIERE_ETAT,
            etat_initial="eteint",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-garage-lumiere")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("allume", "on", "1"):
            print("[garage-lumiere] 💡 Lumière allumée")
            return "allume"
        if commande in ("eteint", "off", "0"):
            print("[garage-lumiere] 💡 Lumière éteinte")
            return "eteint"
        return self.etat


if __name__ == "__main__":
    ActionneurGarageLumiere().demarrer()

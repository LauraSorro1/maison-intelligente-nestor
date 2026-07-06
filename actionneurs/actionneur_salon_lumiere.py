"""Actionneur de la lumière du salon — classe Python.

S'abonne à maison/salon/lumiere/cmd et réagit aux commandes
"allume"/"eteint". Publie son état sur maison/salon/lumiere/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_salon_lumiere
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurSalonLumiere(Actionneur):
    def __init__(self):
        super().__init__(
            nom="salon-lumiere",
            sujet_cmd=config.SujetsActionneurs.SALON_LUMIERE_CMD,
            sujet_etat=config.SujetsActionneurs.SALON_LUMIERE_ETAT,
            etat_initial="eteint",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-salon-lumiere")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("allume", "on", "1"):
            print("[salon-lumiere] 💡 Lumière allumée")
            return "allume"
        if commande in ("eteint", "off", "0"):
            print("[salon-lumiere] 💡 Lumière éteinte")
            return "eteint"
        return self.etat


if __name__ == "__main__":
    ActionneurSalonLumiere().demarrer()

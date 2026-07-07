"""Actionneur de la pompe de l'aquarium — classe Python.

S'abonne à maison/salon/aquarium/pompe/cmd et réagit aux commandes
"allume"/"eteint". Publie son état sur maison/salon/aquarium/pompe/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_aquarium_pompe
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurAquariumPompe(Actionneur):
    def __init__(self):
        super().__init__(
            nom="aquarium-pompe",
            sujet_cmd=config.SujetsActionneurs.SALON_AQUARIUM_POMPE_CMD,
            sujet_etat=config.SujetsActionneurs.SALON_AQUARIUM_POMPE_ETAT,
            etat_initial="allume", # la pompe tourne en continu par défaut
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="actionneur-aquarium-pompe")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("allume", "on", "1"):
            print("[aquarium-pompe] POMPE ALLUMÉE")
            return "allume"
        if commande in ("eteint", "off", "0"):
            print("[aquarium-pompe] ⏹️ Pompe éteinte")
            return "eteint"
        return self.etat


if __name__ == "__main__":
    ActionneurAquariumPompe().demarrer()

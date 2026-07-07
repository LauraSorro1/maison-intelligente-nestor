"""Actionneur de la lumière d'UV de l'aquarium — classe Python.

S'abonne à maison/salon/aquarium/uv/cmd et réagit aux commandes
"allume"/"eteint". Publie son état sur maison/salon/aquarium/uv/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_aquarium_uv
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurAquariumUV(Actionneur):
    def __init__(self):
        super().__init__(
            nom="aquarium-uv",
            sujet_cmd=config.SujetsActionneurs.SALON_AQUARIUM_UV_CMD,
            sujet_etat=config.SujetsActionneurs.SALON_AQUARIUM_UV_ETAT,
            etat_initial="allume", # la lumière UV tourne en continu pour stériliser l'eau
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="actionneur-aquarium-uv")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("allume", "on", "1"):
            print("[aquarium-uv] UV ALLUMÉ")
            return "allume"
        if commande in ("eteint", "off", "0"):
            print("[aquarium-uv] ⏹️ UV éteint")
            return "eteint"
        return self.etat


if __name__ == "__main__":
    ActionneurAquariumUV().demarrer()

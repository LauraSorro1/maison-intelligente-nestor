"""Actionneur aquarium — classe Python.

S'abonne à maison/salon/aquarium/cmd et réagit aux commandes
"sonne"/"silence". Publie son état sur maison/salon/aquarium/etat.

CECI EST UN EXEMPLE D'ACTIONNEUR : créez vos propres actionneurs pour
les autres objets.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_aquarium
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurAquarium(Actionneur):
    def __init__(self):
        super().__init__(
            nom="aquarium",
            sujet_cmd=config.SujetsActionneurs.AQUARIUM_CMD,
            sujet_etat=config.SujetsActionneurs.AQUARIUM_ETAT,
            etat_initial="silence",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="actionneur-aquarium")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("sonne", "on", "1"):
            print("[aquarium] 🔔 BIP BIP BIP")
            return "sonne"
        if commande in ("silence", "off", "0"):
            return "silence"
        return self.etat


if __name__ == "__main__":
    ActionneurAquarium().demarrer()

"""Actionneur de la thermopompe de la chambre — classe Python.

S'abonne à maison/chambre/thermopompe/cmd et réagit aux commandes
"chauffe"/"climatise"/"ventile"/"arrete". Publie son état sur maison/chambre/thermopompe/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_chambre_thermopompe
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurChambreThermopompe(Actionneur):
    def __init__(self):
        super().__init__(
            nom="chambre-thermopompe",
            sujet_cmd=config.SujetsActionneurs.CHAMBRE_THERMOPOMPE_CMD,
            sujet_etat=config.SujetsActionneurs.CHAMBRE_THERMOPOMPE_ETAT,
            etat_initial="arrete",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-chambre-thermopompe")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("chauffe", "heat"):
            print("[chambre-thermopompe] 🔥 Chauffage activé")
            return "chauffe"
        if commande in ("climatise", "cool"):
            print("[chambre-thermopompe] ❄️ Climatisation activée")
            return "climatise"
        if commande in ("ventile", "fan"):
            print("[chambre-thermopompe] 💨 Ventilation activée")
            return "ventile"
        if commande in ("arrete", "off", "0"):
            print("[chambre-thermopompe] ⏹️ Thermopompe arrêtée")
            return "arrete"
        return self.etat


if __name__ == "__main__":
    ActionneurChambreThermopompe().demarrer()

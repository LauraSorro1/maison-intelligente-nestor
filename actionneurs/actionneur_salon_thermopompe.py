"""Actionneur de la thermopompe du salon — classe Python.

S'abonne à maison/salon/thermopompe/cmd et réagit aux commandes
"chauffe"/"climatise"/"ventile"/"arrete". Publie son état sur maison/salon/thermopompe/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_salon_thermopompe
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurSalonThermopompe(Actionneur):
    def __init__(self):
        super().__init__(
            nom="salon-thermopompe",
            sujet_cmd=config.SujetsActionneurs.SALON_THERMOPOMPE_CMD,
            sujet_etat=config.SujetsActionneurs.SALON_THERMOPOMPE_ETAT,
            etat_initial="arrete",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-salon-thermopompe")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("chauffe", "heat"):
            print("[salon-thermopompe] 🔥 Chauffage activé")
            return "chauffe"
        if commande in ("climatise", "cool"):
            print("[salon-thermopompe] ❄️ Climatisation activée")
            return "climatise"
        if commande in ("ventile", "fan"):
            print("[salon-thermopompe] 💨 Ventilation activée")
            return "ventile"
        if commande in ("arrete", "off", "0"):
            print("[salon-thermopompe] ⏹️ Thermopompe arrêtée")
            return "arrete"
        return self.etat


if __name__ == "__main__":
    ActionneurSalonThermopompe().demarrer()

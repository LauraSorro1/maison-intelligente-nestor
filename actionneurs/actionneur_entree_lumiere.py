"""Actionneur de la lumière de l'entrée — classe Python.

S'abonne à maison/entree/lumiere/cmd et réagit aux commandes
"allume"/"eteint". Publie son état sur maison/entree/lumiere/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_entree_lumiere
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurEntreeLumiere(Actionneur):
    def __init__(self):
        super().__init__(
            nom="entree-lumiere",
            sujet_cmd=config.SujetsActionneurs.ENTREE_LUMIERE_CMD,
            sujet_etat=config.SujetsActionneurs.ENTREE_LUMIERE_ETAT,
            etat_initial="eteint",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-entree-lumiere")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("allume", "on", "1"):
            print("[entree-lumiere] 💡 Lumière allumée")
            return "allume"
        if commande in ("eteint", "off", "0"):
            print("[entree-lumiere] 💡 Lumière éteinte")
            return "eteint"
        return self.etat


if __name__ == "__main__":
    ActionneurEntreeLumiere().demarrer()

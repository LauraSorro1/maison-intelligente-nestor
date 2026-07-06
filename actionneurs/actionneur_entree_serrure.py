"""Actionneur de la serrure de l'entrée — classe Python.

S'abonne à maison/entree/serrure/cmd et réagit aux commandes
"verrouille"/"deverrouille". Publie son état sur maison/entree/serrure/etat.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m actionneurs.actionneur_entree_serrure
"""
import config
import paho.mqtt.client as mqtt
from actionneurs.base_actionneur import Actionneur


class ActionneurEntreeSerrure(Actionneur):
    def __init__(self):
        super().__init__(
            nom="entree-serrure",
            sujet_cmd=config.SujetsActionneurs.ENTREE_SERRURE_CMD,
            sujet_etat=config.SujetsActionneurs.ENTREE_SERRURE_ETAT,
            etat_initial="deverrouille",
            client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
            client_id="actionneur-entree-serrure")
        )

    def appliquer(self, commande):
        commande = commande.lower()
        if commande in ("verrouille", "lock", "1"):
            print("[entree-serrure] 🔒 Serrure verrouillée")
            return "verrouille"
        if commande in ("deverrouille", "unlock", "0"):
            print("[entree-serrure] 🔓 Serrure déverrouillée")
            return "deverrouille"
        return self.etat


if __name__ == "__main__":
    ActionneurEntreeSerrure().demarrer()

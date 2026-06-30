"""Classe de base pour tous les capteurs simulés.

Chaque capteur est une classe Python qui hérite de Capteur et redéfinit
la méthode `lire()`. La classe de base s'occupe de la connexion MQTT, de
la boucle de publication périodique et du formatage du message JSON.
"""
import json
import time
from datetime import datetime

import config


class Capteur:
    """Capteur MQTT générique.

    Sous-classer et redéfinir `lire()` pour produire une nouvelle valeur
    à chaque cycle. La sous-classe construit et fournit son propre client
    MQTT (`client`), ce qui lui permet de régler à sa guise le last will,
    le QoS, le mode retain, etc. avant de le passer ici.
    """

    def __init__(self, type_capteur, sujet, unite, periode, client):
        self.type_capteur = type_capteur
        self.sujet = sujet
        self.unite = unite
        self.periode = periode
        self.client = client

    def lire(self):
        """Retourne la prochaine valeur du capteur.

        À redéfinir dans chaque sous-classe.
        """
        raise NotImplementedError

    def construire_message(self, valeur):
        return {
            "type": self.type_capteur,
            "valeur": valeur,
            "unite": self.unite,
            "horodatage": datetime.now().isoformat(timespec="seconds"),
        }

    def demarrer(self):
        """Connexion au courtier puis boucle de publication infinie."""
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        print(f"[{self.type_capteur}] démarré → {self.sujet} (Ctrl+C pour arrêter).")
        try:
            while True:
                #*DONE: simuler la lecture du capteur et publier le message JSON sur le sujet MQTT à un interval de temps défini par self.periode
                valeur = self.lire()
                message = json.dumps(self.construire_message(valeur))
                self.client.publish(self.sujet, message)
                time.sleep(self.periode)
                pass
        except KeyboardInterrupt:
            print(f"\n[{self.type_capteur}] arrêté.")
        finally:
            self.client.disconnect()

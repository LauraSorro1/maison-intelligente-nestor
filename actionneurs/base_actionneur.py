"""Classe de base pour tous les actionneurs simulés.

Un actionneur est une classe Python qui s'abonne à un sujet de commande
MQTT (`.../cmd`) et réagit aux messages reçus. Après chaque changement, il
publie son état courant sur un sujet d'état (`.../etat`) afin que le
tableau de bord reste synchronisé.
"""
import json

import paho.mqtt.client as mqtt

import config


class Actionneur:
    """Actionneur MQTT générique.

    Sous-classer et redéfinir `appliquer(commande)`, qui reçoit la chaîne
    de commande et retourne le nouvel état (chaîne) à publier.
    """

    def __init__(self, nom, sujet_cmd, sujet_etat, etat_initial, client):
        self.nom = nom
        self.sujet_cmd = sujet_cmd
        self.sujet_etat = sujet_etat
        self.etat = etat_initial
        self.client = client
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def appliquer(self, commande):
        """Traite une commande et retourne le nouvel état. À redéfinir."""
        raise NotImplementedError

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        #paho-mqtt retourne un reason_code de 0 si la connection est réussie, sinon un code d'erreur.
        if reason_code == 0:
            client.subscribe(self.sujet_cmd)
            print(f"[{self.nom}] abonné à {self.sujet_cmd}")
            self._publier_etat()
        else:
            print(f"[{self.nom}] échec de connexion MQTT (code {reason_code})")

    def _on_message(self, client, userdata, msg):
        texte = msg.payload.decode("utf-8")
        # La commande peut être un JSON {"commande": "..."} ou une chaîne brute.
        try:
            commande = json.loads(texte).get("commande", texte)
        except json.JSONDecodeError:
            commande = texte.strip()

        ancien = self.etat
        self.etat = self.appliquer(commande)
        print(f"[{self.nom}] commande={commande!r} : {ancien} -> {self.etat}")
        self._publier_etat()

    def _publier_etat(self):
        #TODO: Publier l'état courant sur le sujet MQTT self.sujet_etat. Le message doit être un JSON {"etat": "..."}.
        pass

    def demarrer(self):
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        print(f"[{self.nom}] démarré (Ctrl+C pour arrêter).")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print(f"\n[{self.nom}] arrêté.")
        finally:
            self.client.disconnect()

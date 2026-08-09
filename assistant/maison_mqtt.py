import paho.mqtt.client as mqtt
import config
import json

class MaisonMQTT:
    """Pont entre l'assistant vocal et l'infrastructure MQTT du Projet 1.

    - Publie les commandes ON/OFF sur les topics des actionneurs.
    - S'abonne aux topics des capteurs et retient la derniere valeur connue.
    """

    def __init__(self):

        #TODO: Ajoutez vos capteurs et actionneurs avec leurs sujets MQTT
        self.topics_capteurs = {
            "maison/salon/aquarium/temperature": "temperature_aquarium",
        }

        self.topics_actionneurs = {
            "alarme": "maison/salon/aquarium/cmd"
        }

        self.dernieres_valeurs = {}

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="assistant-maison")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Assistant connecte au broker MQTT")
            # TODO: S'abonner aux topics des capteurs
        else:
            print(f"Erreur de connexion : {rc}")

    def on_message(self, client, userdata, message):
        capteur = self.topics_capteurs.get(message.topic)

        if capteur:
            msg = message.payload.decode()
            self.dernieres_valeurs[capteur] = json.loads(msg).get("valeur")

    def demarrer(self):
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        self.client.loop_start()

    def arreter(self):
        self.client.loop_stop()
        self.client.disconnect()

    def commander(self, appareil, action):
        # TODO: publier la commande sur le topic de l'actionneur visé
        pass

    def lire(self, capteur):
        """Retourne la derniere valeur connue du capteur (ou None)."""
        return self.dernieres_valeurs.get(capteur)

import paho.mqtt.client as mqtt
import config
import json

class MaisonMQTT:
    """Pont entre l'assistant vocal et l'infrastructure MQTT du Projet 1.

    - Publie les commandes ON/OFF sur les topics des actionneurs.
    - S'abonne aux topics des capteurs et retient la derniere valeur connue.
    """

    def __init__(self):

        # * DONE: Ajoutez vos capteurs et actionneurs avec leurs sujets MQTT
        # Sujets des capteurs surveillés -> nom officiel du capteur
        self.topics_capteurs = {
            config.SujetsCapteurs.SALON_AQUARIUM_TEMPERATURE.value: "temperature_aquarium",
            config.SujetsCapteurs.SALON_TEMPERATURE.value: "temperature_salon",
        }

        # Nom officiel de l'actionneur -> sujet de commande MQTT
        self.topics_actionneurs = {
            "aquarium_pompe": config.SujetsActionneurs.SALON_AQUARIUM_POMPE_CMD.value,
            "aquarium_uv":    config.SujetsActionneurs.SALON_AQUARIUM_UV_CMD.value,
            "entree_serrure": config.SujetsActionneurs.ENTREE_SERRURE_CMD.value,
        }

        self.dernieres_valeurs = {}

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="assistant-maison")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Assistant connecte au broker MQTT")
            # * DONE: S'abonner aux topics des capteurs
            for topic in self.topics_capteurs.keys():
                client.subscribe(topic)
        else:
            print(f"Erreur de connexion : {reason_code}")

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

    # Traduction (appareil, action ON/OFF) -> commande comprise par l'actionneur.
    # La serrure parle « verrouille/deverrouille », les autres « allume/eteint ».
    COMMANDES = {
        "aquarium_pompe": {"ON": "allume",     "OFF": "eteint"},
        "aquarium_uv":    {"ON": "allume",     "OFF": "eteint"},
        "entree_serrure": {"ON": "verrouille", "OFF": "deverrouille"},
    }

    def commander(self, appareil, action):
        # * DONE: publier la commande sur le topic de l'actionneur visé
        """Publie la commande sur le topic de l'actionneur vise (format JSON,
        identique a celui du controleur du Projet 1)."""
        sujet = self.topics_actionneurs.get(appareil)
        commande = self.COMMANDES.get(appareil, {}).get(action)
        if sujet and commande:
            self.client.publish(sujet, json.dumps({"commande": commande}))

    def lire(self, capteur):
        """Retourne la derniere valeur connue du capteur (ou None)."""
        return self.dernieres_valeurs.get(capteur)

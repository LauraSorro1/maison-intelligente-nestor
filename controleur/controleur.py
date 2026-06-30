"""Contrôleur abonné-publieur — classe Python (cœur du Projet 1).

Le contrôleur assume SIMULTANÉMENT les deux rôles du modèle
publish-subscribe :

  • ABONNÉ : il s'abonne à chaque sujet de capteur (voir config.SujetsCapteurs)
    (une table par capteur).

  • PUBLIEUR : il applique des règles d'automatisation et publie des
    commandes vers les sujets auxquels les actionneurs sont abonnés
    (p. ex. faire sonner l'alarme de l'aquarium).

CECI EST UN SQUELETTE : une seule règle d'exemple est fournie (la
température de l'aquarium). Ajoutez vos propres règles pour vos capteurs.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m controleur.controleur
"""
import json

import paho.mqtt.client as mqtt

import config



# Bornes de température considérées comme normales (°C) pour l'aquarium.
TEMP_MIN = 16.0
TEMP_MAX = 26.0


class Controleur:
    def __init__(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="controleur"
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Mémoire d'état pour éviter de republier/alerter en boucle.
        # Je l'utilise dans l'exemple de règle de température, mais vous pouvez/devez en ajouter d'autres.
        self.temperature_aquarium_hors_plage = False

    # ----- Connexion / abonnement -----
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"Contrôleur connecté au courtier {config.MQTT_HOST}:{config.MQTT_PORT}")
            # TODO: abonnez-vous à chaque sujet capteur (voir config.SujetsCapteurs)
            client.subscribe(config.SujetsCapteurs.SALON_TEMPERATURE.value)
            client.subscribe(config.SujetsCapteurs.SALON_LUMINOSITE.value)
            client.subscribe(config.SujetsCapteurs.CHAMBRE_TEMPERATURE.value)
            client.subscribe(config.SujetsCapteurs.CHAMBRE_HUMIDITE.value)
            client.subscribe(config.SujetsCapteurs.ENTREE_MOUVEMENT.value)
            client.subscribe(config.SujetsCapteurs.ENTREE_PORTE.value)
            client.subscribe(config.SujetsCapteurs.GARAGE_TEMPERATURE.value)
            client.subscribe(config.SujetsCapteurs.GARAGE_VEHICULE.value)
        else:
            print(f"Échec de connexion MQTT (code {reason_code})")

    # ----- Réception d'un message capteur -----
    def _on_message(self, client, userdata, msg):
        texte = msg.payload.decode("utf-8")
        # Premièrement, on s'assure que le message est un JSON valide et qu'il contient les champs attendus.
        # Ensuite, on extrait le type de capteur, la valeur et l'unité (si présente) pour les étapes suivantes.
        try:
            message = json.loads(texte)
            type_capteur = message["type"]
            valeur = message["valeur"]
            unite = message.get("unite", "")
        except (json.JSONDecodeError, KeyError):
            print(f"Message ignoré (format inattendu) sur {msg.topic} : {texte}")
            return

        # 1) Journaliser dans MariaDB (une table par capteur).
        # Comme discuté en classe, la journalisation est repoussée au projet 2. Vous pouvez décommenter la ligne ci-dessous quand vous aurez implémenté la fonction _journaliser().
        # self._journaliser(type_capteur, valeur, unite, msg.topic)

        # 2) Appliquer les règles d'automatisation.
        if type_capteur == "temperature_aquarium":
            self._regle_temperature(valeur)
        # elif type_capteur == "...":     # ← ajoutez vos règles ici

    #  Comme discuté en classe, la journalisation est repoussée au projet 2
    #def _journaliser(self, type_capteur, valeur, unite, sujet):
    #     # TODO: insérer la lecture dans la table MariaDB correspondante au capteur.
    #     #       Astuce : importez db et appelez db.inserer_lecture(type_capteur, valeur, unite).
    #     pass

    # ----- Règle d'exemple : Température hors plage → actionneur + alerte -----
    def _regle_temperature(self, valeur):
        try:
            t = float(valeur)
        except (TypeError, ValueError):
            return
        hors_plage = t < TEMP_MIN or t > TEMP_MAX
        if hors_plage and not self.temperature_aquarium_hors_plage:
            self._publier_commande(config.SujetsActionneurs.AQUARIUM_CMD, "sonne")
            self.temperature_aquarium_hors_plage = True
            print(f"RÈGLE: température hors plage ({t} °C) → l'alarme de l'aquarium sonne")
        elif not hors_plage and self.temperature_aquarium_hors_plage:
            self._publier_commande(config.SujetsActionneurs.AQUARIUM_CMD, "silence")
            self.temperature_aquarium_hors_plage = False
            print("RÈGLE: température revenue à la normale → l'alarme de l'aquarium s'arrête")

    def _publier_commande(self, sujet, commande):
        #*DONE: publier la commande sur le sujet actionneur
        self.client.publish(sujet, json.dumps({"commande": commande}))
        pass

    def demarrer(self):
        #*DONE: connecter au courtier et lancer la boucle MQTT
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        print("Contrôleur démarré (Ctrl+C pour arrêter).")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\nContrôleur arrêté.")
        finally:
            self.client.disconnect()


if __name__ == "__main__":
    Controleur().demarrer()

"""Contrôleur abonné-publieur — classe Python (cœur du Projet 1).

Le contrôleur assume SIMULTANÉMENT les deux rôles du modèle
publish-subscribe :

  • ABONNÉ : il s'abonne à chaque sujet de capteur (voir config.SujetsCapteurs)
    (une table par capteur).

  • PUBLIEUR : il applique des règles d'automatisation et publie des
    commandes vers les sujets auxquels les actionneurs sont abonnés
    (p. ex. faire sonner l'alarme de l'aquarium).

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m controleur.controleur
"""
import json
import paho.mqtt.client as mqtt
import config
from datetime import datetime
import time


# Salon
SALON_TEMP_MIN = 18.0
SALON_TEMP_MAX = 23.0
SALON_LUX_MIN = 200.0

# Chambre
CHAMBRE_TEMP_MIN = 16.0
CHAMBRE_TEMP_MAX = 23.0

# Garage
GARAGE_TEMP_MIN = 5.0
GARAGE_TEMP_MAX = 7.0

# Alertes
SUJET_ALERTES = "maison/alertes"
HEURE_NUIT_DEBUT = 23 # heures
HEURE_NUIT_FIN = 5 # heures
PORTE_OUVERTE_MAX = 30 # secondes

class Controleur:
    def __init__(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="controleur"
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Mémoire d'état pour éviter de republier/alerter en boucle.
        self.salon_lumiere_allumee = False
        self.salon_thermopompe_etat = "arrete"
        self.chambre_thermopompe_etat = "arrete"
        self.entree_lumiere_allumee = False
        self.entree_serrure_verrouillee = False
        self.garage_chauffage_allume = False
        self.garage_porte_ouverte = False

        # Variables d'état.
        self.entree_porte_ouverte_depuis = None # timestamp d'ouverture
        self.alerte_porte_envoyee = False # pour éviter d'envoyer plusieurs alertes
        self.alerte_temp_salon_envoyee = False

    # ----- Connexion / abonnement -----
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"Contrôleur connecté au courtier {config.MQTT_HOST}:{config.MQTT_PORT}")
            # *DONE: abonnés à chaque sujet capteur (voir config.SujetsCapteurs)
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
        if type_capteur == "temperature_salon":
            self._regle_salon_temperature(valeur)
        elif type_capteur == "luminosite_salon":
            self._regle_salon_luminosite(valeur)
        elif type_capteur == "temperature_chambre":
            self._regle_chambre_temperature(valeur)
        elif type_capteur == "mouvement_entree":
            self._regle_entree_mouvement(valeur)
        elif type_capteur == "temperature_garage":
            self._regle_garage_temperature(valeur)
        elif type_capteur == "vehicule_garage":
            self._regle_garage_vehicule(valeur)
        elif type_capteur == "porte_entree":
            self._regle_entree_porte(valeur)

    #  Comme discuté en classe, la journalisation est repoussée au projet 2
    #def _journaliser(self, type_capteur, valeur, unite, sujet):
    #     # TODO: insérer la lecture dans la table MariaDB correspondante au capteur.
    #     #       Astuce : importez db et appelez db.inserer_lecture(type_capteur, valeur, unite).
    #     pass

    def _regle_salon_luminosite(self, valeur):
        try:
            lux = float(valeur)
        except (TypeError, ValueError):
            return
        if lux < SALON_LUX_MIN and not self.salon_lumiere_allumee:
            self._publier_commande(config.SujetsActionneurs.SALON_LUMIERE_CMD, "allume")
            self.salon_lumiere_allumee = True
            print(f"RÈGLE: luminosité trop basse ({lux} lux) → lumière salon allumée")
        elif lux >= SALON_LUX_MIN and self.salon_lumiere_allumee:
            self._publier_commande(config.SujetsActionneurs.SALON_LUMIERE_CMD, "eteint")
            self.salon_lumiere_allumee = False
            print(f"RÈGLE: luminosité suffisante ({lux} lux) → lumière salon éteinte")

    def _regle_salon_temperature(self, valeur):
        try:
            temp = float(valeur)
        except (TypeError, ValueError):
            return
        if temp < SALON_TEMP_MIN and self.salon_thermopompe_etat != "chauffe":
            self._publier_commande(config.SujetsActionneurs.SALON_THERMOPOMPE_CMD, "chauffe")
            self.salon_thermopompe_etat = "chauffe"
            print(f"RÈGLE: température trop basse ({temp}°C) → thermopompe salon chauffe")
            if not self.alerte_temp_salon_envoyee:
                self._publier_alerte(f"température salon hors plage ({temp}°C)")
                self.alerte_temp_salon_envoyee = True
        elif temp > SALON_TEMP_MAX and self.salon_thermopompe_etat!= "climatise":
            self._publier_commande(config.SujetsActionneurs.SALON_THERMOPOMPE_CMD, "climatise")
            self.salon_thermopompe_etat = "climatise"
            print(f"RÈGLE: température trop haute ({temp}°C) → thermopompe salon climatise")
            if not self.alerte_temp_salon_envoyee:
                self._publier_alerte(f"température salon hors plage ({temp}°C)")
                self.alerte_temp_salon_envoyee = True
        elif SALON_TEMP_MIN <= temp <= SALON_TEMP_MAX and self.salon_thermopompe_etat != "arrete":
            self._publier_commande(config.SujetsActionneurs.SALON_THERMOPOMPE_CMD, "arrete")
            self.salon_thermopompe_etat = "arrete"
            print(f"RÈGLE: température dans la plage ({temp}°C) → thermopompe salon arrêtée")
            self.alerte_temp_salon_envoyee = False # réinitialiser l'alerte pour la prochaine fois que la température sortira de la plage

    def _regle_chambre_temperature(self, valeur):
        try:
            temp = float(valeur)
        except (TypeError, ValueError):
            return
        if temp < CHAMBRE_TEMP_MIN and self.chambre_thermopompe_etat != "chauffe":
            self._publier_commande(config.SujetsActionneurs.CHAMBRE_THERMOPOMPE_CMD, "chauffe")
            self.chambre_thermopompe_etat = "chauffe"
            print(f"RÈGLE: température trop basse ({temp}°C) → thermopompe chambre chauffe")
        elif temp > CHAMBRE_TEMP_MAX and self.chambre_thermopompe_etat!= "climatise":
            self._publier_commande(config.SujetsActionneurs.CHAMBRE_THERMOPOMPE_CMD, "climatise")
            self.chambre_thermopompe_etat = "climatise"
            print(f"RÈGLE: température trop haute ({temp}°C) → thermopompe chambre climatise")
        elif CHAMBRE_TEMP_MIN <= temp <= CHAMBRE_TEMP_MAX and self.chambre_thermopompe_etat != "arrete":
            self._publier_commande(config.SujetsActionneurs.CHAMBRE_THERMOPOMPE_CMD, "arrete")
            self.chambre_thermopompe_etat = "arrete"
            print(f"RÈGLE: température dans la plage ({temp}°C) → thermopompe chambre arrêtée")

    def _regle_entree_porte(self, valeur):
        if valeur == "ouvert":
            if self.entree_porte_ouverte_depuis is None:
                self.entree_porte_ouverte_depuis = time.time()
                print("RÈGLE: porte entrée ouverte → surveillance démarrée")
            elif time.time() - self.entree_porte_ouverte_depuis > 30 and not self.alerte_porte_envoyee:
                self._publier_alerte("porte entrée ouverte trop longtemps")
                self.alerte_porte_envoyee = True
        elif valeur == "ferme":
            self.entree_porte_ouverte_depuis = None
            self.alerte_porte_envoyee = False
            print("RÈGLE: porte entrée fermée → surveillance réinitialisée")

    def _regle_entree_mouvement(self, valeur):
        try:
            mouvement = int(valeur)
        except (TypeError, ValueError):
            return
        if mouvement == 1 and not self.entree_lumiere_allumee:
            self._publier_commande(config.SujetsActionneurs.ENTREE_LUMIERE_CMD, "allume")
            self.entree_lumiere_allumee = True
            print(f"RÈGLE: mouvement détecté → lumière entrée allumée")
            self._publier_commande(config.SujetsActionneurs.ENTREE_SERRURE_CMD, "verrouille")
            self.entree_serrure_verrouillee = True
            print(f"RÈGLE: mouvement détecté → serrure entrée verrouillée")
            # alerte nocturne
            heure = datetime.now().hour
            if (heure >= HEURE_NUIT_DEBUT or heure < HEURE_NUIT_FIN):
                self._publier_alerte("Mouvement détecté à l'entrée pendant la nuit")
        elif mouvement == 0 and self.entree_lumiere_allumee:
            self._publier_commande(config.SujetsActionneurs.ENTREE_LUMIERE_CMD, "eteint")
            self.entree_lumiere_allumee = False
            print(f"RÈGLE: pas de mouvement → lumière entrée éteinte")
            self._publier_commande(config.SujetsActionneurs.ENTREE_SERRURE_CMD, "deverrouille")
            self.entree_serrure_verrouillee = False
            print(f"RÈGLE: pas de mouvement → serrure entrée déverrouillée")

    def _regle_garage_temperature(self, valeur):
        try:
            temp = float(valeur)
        except (TypeError, ValueError):
            return
        if temp < GARAGE_TEMP_MIN and not self.garage_chauffage_allume:
            self.garage_chauffage_allume = True
            self._publier_commande(config.SujetsActionneurs.GARAGE_CHAUFFAGE_CMD, "allume")
            print(f"RÈGLE: température trop basse ({temp}°C) → chauffage garage allumé")
        elif temp >= GARAGE_TEMP_MAX and self.garage_chauffage_allume:
            self.garage_chauffage_allume = False
            self._publier_commande(config.SujetsActionneurs.GARAGE_CHAUFFAGE_CMD, "eteint")
            print(f"RÈGLE: température dans la plage ({temp}°C) → chauffage garage arrêté")

    def _regle_garage_vehicule(self, valeur):
        try:
            mouvement = int(valeur)
        except (TypeError, ValueError):
            return
        if mouvement == 1 and not self.garage_porte_ouverte:
            self.garage_porte_ouverte = True
            self._publier_commande(config.SujetsActionneurs.GARAGE_PORTE_CMD, "ouvre")
            print(f"RÈGLE: véhicule détecté → porte garage ouverte")
            self._publier_alerte("Véhicule détecté dans le garage")
        elif mouvement == 0 and self.garage_porte_ouverte:
            self.garage_porte_ouverte = False
            self._publier_commande(config.SujetsActionneurs.GARAGE_PORTE_CMD, "ferme")
            print(f"RÈGLE: pas de véhicule → porte garage fermée")

    def _publier_commande(self, sujet, commande):
        #*DONE: publier la commande sur le sujet actionneur
        self.client.publish(sujet, json.dumps({"commande": commande}))

    def _publier_alerte(self, message):
        alerte = json.dumps({
            "alerte": message, 
            "horodatage": datetime.now().isoformat(timespec="seconds")
        })
        self.client.publish(SUJET_ALERTES, alerte, qos=1, retain=False)
        print(f"🚨 ALERTE: {message}")

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

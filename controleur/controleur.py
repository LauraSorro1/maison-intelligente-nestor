"""Contrôleur abonné-publieur — classe Python (cœur du Projet 1).

Le contrôleur assume SIMULTANÉMENT les deux rôles du modèle
publish-subscribe :

  • ABONNÉ : il s'abonne à chaque sujet de capteur (voir config.SujetsCapteurs)

  • PUBLIEUR : il applique des règles d'automatisation et publie des
    commandes vers les sujets auxquels les actionneurs sont abonnés.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m controleur.controleur
"""
import json
import paho.mqtt.client as mqtt
import config


# Salon
SALON_TEMP_MIN = 18.0
SALON_TEMP_MAX = 23.0
SALON_LUX_MIN  = 200.0

# Aquarium — plage normale eau douce (source : aquariophilie-aquarium.fr)
AQUARIUM_PH_MIN     = 6.8
AQUARIUM_PH_MAX     = 7.5
AQUARIUM_NIVEAU_MIN = 70.0  # % — UV s'éteint si niveau bas

# Garage — norme minimale Ville de Montréal (Règlement 03-096)
GARAGE_TEMP_MIN = 15.0
GARAGE_TEMP_MAX = 17.0
GARAGE_CO_MAX   = 25.0  # ppm — seuil Santé Canada

# Codes-barres autorisés pour l'ouverture de la porte du garage
CODES_AUTORISES = ["AUTO-001", "AUTO-002", "AUTO-003"]


class Controleur:
    def __init__(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="controleur"
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Mémoire d'état pour éviter de republier en boucle.
        self.salon_lumiere_allumee    = False
        self.salon_thermopompe_etat   = "arrete"
        self.entree_lumiere_allumee   = False
        self.entree_serrure_verrouillee = True   # verrouillée par défaut
        self.garage_chauffage_allume  = False
        self.garage_porte_ouverte     = False
        self.garage_lumiere_allumee   = False
        self.garage_vehicule_present  = False
        self.garage_barcode_valide    = False
        self.aquarium_pompe_allumee   = True     # pompe tourne en continu
        self.aquarium_uv_allumee      = True     # UV allumé en continu

    # ----- Connexion / abonnement -----
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"Contrôleur connecté au courtier {config.MQTT_HOST}:{config.MQTT_PORT}")
            # Salon
            client.subscribe(config.SujetsCapteurs.SALON_TEMPERATURE.value)
            client.subscribe(config.SujetsCapteurs.SALON_LUMINOSITE.value)
            client.subscribe(config.SujetsCapteurs.SALON_HUMIDITE.value)
            # Aquarium
            client.subscribe(config.SujetsCapteurs.SALON_AQUARIUM_TEMPERATURE.value)
            client.subscribe(config.SujetsCapteurs.SALON_AQUARIUM_PH.value)
            client.subscribe(config.SujetsCapteurs.SALON_AQUARIUM_NIVEAU.value)
            # Entrée
            client.subscribe(config.SujetsCapteurs.ENTREE_MOUVEMENT.value)
            client.subscribe(config.SujetsCapteurs.ENTREE_PORTE.value)
            # Garage
            client.subscribe(config.SujetsCapteurs.GARAGE_TEMPERATURE.value)
            client.subscribe(config.SujetsCapteurs.GARAGE_CO.value)
            client.subscribe(config.SujetsCapteurs.GARAGE_VEHICULE.value)
            client.subscribe(config.SujetsCapteurs.GARAGE_BARCODE.value)
        else:
            print(f"Échec de connexion MQTT (code {reason_code})")

    # ----- Réception d'un message capteur -----
    def _on_message(self, client, userdata, msg):
        texte = msg.payload.decode("utf-8")
        try:
            message = json.loads(texte)
            type_capteur = message["type"]
            valeur = message["valeur"]
            unite = message.get("unite", "")
        except (json.JSONDecodeError, KeyError):
            print(f"Message ignoré (format inattendu) sur {msg.topic} : {texte}")
            return

        # Journalisation MariaDB repoussée au Projet 2.
        # self._journaliser(type_capteur, valeur, unite, msg.topic)

        # Appliquer les règles d'automatisation.
        if type_capteur == "temperature_salon":
            self._regle_salon_temperature(valeur)
        elif type_capteur == "luminosite_salon":
            self._regle_salon_luminosite(valeur)
        elif type_capteur == "humidite_salon":
            pass  # surveillé mais pas de règle automatique
        elif type_capteur == "temperature_aquarium":
            pass  # surveillé mais pas de règle automatique
        elif type_capteur == "ph_aquarium":
            self._regle_aquarium_ph(valeur)
        elif type_capteur == "niveau_aquarium":
            self._regle_aquarium_niveau(valeur)
        elif type_capteur == "mouvement_entree":
            self._regle_entree_mouvement(valeur)
        elif type_capteur == "porte_entree":
            pass  # surveillé mais pas de règle automatique
        elif type_capteur == "temperature_garage":
            self._regle_garage_temperature(valeur)
        elif type_capteur == "co_garage":
            self._regle_garage_co(valeur)
        elif type_capteur == "vehicule_garage":
            self._regle_garage_vehicule(valeur)
        elif type_capteur == "barcode_garage":
            self._regle_garage_barcode(valeur)

    # Journalisation repoussée au Projet 2.
    # def _journaliser(self, type_capteur, valeur, unite, sujet):
    #     pass

    # ----- Règles — Salon -----

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
        elif temp > SALON_TEMP_MAX and self.salon_thermopompe_etat != "climatise":
            self._publier_commande(config.SujetsActionneurs.SALON_THERMOPOMPE_CMD, "climatise")
            self.salon_thermopompe_etat = "climatise"
            print(f"RÈGLE: température trop haute ({temp}°C) → thermopompe salon climatise")
        elif SALON_TEMP_MIN <= temp <= SALON_TEMP_MAX and self.salon_thermopompe_etat != "arrete":
            self._publier_commande(config.SujetsActionneurs.SALON_THERMOPOMPE_CMD, "arrete")
            self.salon_thermopompe_etat = "arrete"
            print(f"RÈGLE: température dans la plage ({temp}°C) → thermopompe salon arrêtée")

    # ----- Règles — Aquarium -----

    def _regle_aquarium_ph(self, valeur):
        try:
            ph = float(valeur)
        except (TypeError, ValueError):
            return
        if ph < AQUARIUM_PH_MIN or ph > AQUARIUM_PH_MAX:
            print(f"RÈGLE: pH hors plage ({ph}) → surveillance requise")

    def _regle_aquarium_niveau(self, valeur):
        try:
            niveau = float(valeur)
        except (TypeError, ValueError):
            return
        if niveau < AQUARIUM_NIVEAU_MIN and self.aquarium_uv_allumee:
            self._publier_commande(config.SujetsActionneurs.SALON_AQUARIUM_UV_CMD, "eteint")
            self.aquarium_uv_allumee = False
            print(f"RÈGLE: niveau aquarium bas ({niveau}%) → UV éteint (protection)")
        elif niveau >= AQUARIUM_NIVEAU_MIN and not self.aquarium_uv_allumee:
            self._publier_commande(config.SujetsActionneurs.SALON_AQUARIUM_UV_CMD, "allume")
            self.aquarium_uv_allumee = True
            print(f"RÈGLE: niveau aquarium suffisant ({niveau}%) → UV allumé")

    # ----- Règles — Entrée -----

    def _regle_entree_mouvement(self, valeur):
        try:
            mouvement = int(valeur)
        except (TypeError, ValueError):
            return
        if mouvement == 1 and not self.entree_lumiere_allumee:
            self._publier_commande(config.SujetsActionneurs.ENTREE_LUMIERE_CMD, "allume")
            self.entree_lumiere_allumee = True
            print("RÈGLE: mouvement détecté → lumière entrée allumée")
        elif mouvement == 0 and self.entree_lumiere_allumee:
            self._publier_commande(config.SujetsActionneurs.ENTREE_LUMIERE_CMD, "eteint")
            self.entree_lumiere_allumee = False
            print("RÈGLE: pas de mouvement → lumière entrée éteinte")

    # ----- Règles — Garage -----

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
            print(f"RÈGLE: température suffisante ({temp}°C) → chauffage garage éteint")

    def _regle_garage_co(self, valeur):
        try:
            co = float(valeur)
        except (TypeError, ValueError):
            return
        if co > GARAGE_CO_MAX and not self.garage_porte_ouverte:
            self.garage_porte_ouverte = True
            self._publier_commande(config.SujetsActionneurs.GARAGE_PORTE_CMD, "ouvre")
            print(f"RÈGLE: CO dangereux ({co} ppm > {GARAGE_CO_MAX} ppm) → porte garage ouverte")

    def _regle_garage_vehicule(self, valeur):
        try:
            vehicule = int(valeur)
        except (TypeError, ValueError):
            return
        if vehicule == 1 and not self.garage_vehicule_present:
            self.garage_vehicule_present = True
            print("RÈGLE: véhicule détecté → en attente du code-barres")
        elif vehicule == 0 and self.garage_vehicule_present:
            self.garage_vehicule_present = False
            self.garage_barcode_valide = False
            if self.garage_porte_ouverte:
                self.garage_porte_ouverte = False
                self._publier_commande(config.SujetsActionneurs.GARAGE_PORTE_CMD, "ferme")
                print("RÈGLE: véhicule parti → porte garage fermée")
            if self.garage_lumiere_allumee:
                self.garage_lumiere_allumee = False
                self._publier_commande(config.SujetsActionneurs.GARAGE_LUMIERE_CMD, "eteint")
                print("RÈGLE: véhicule parti → lumière garage éteinte")

    def _regle_garage_barcode(self, valeur):
        if self.garage_vehicule_present and valeur in CODES_AUTORISES:
            self.garage_barcode_valide = True
            if not self.garage_porte_ouverte:
                self.garage_porte_ouverte = True
                self._publier_commande(config.SujetsActionneurs.GARAGE_PORTE_CMD, "ouvre")
                print(f"RÈGLE: code-barres valide ({valeur}) → porte garage ouverte")
            if not self.garage_lumiere_allumee:
                self.garage_lumiere_allumee = True
                self._publier_commande(config.SujetsActionneurs.GARAGE_LUMIERE_CMD, "allume")
                print(f"RÈGLE: code-barres valide ({valeur}) → lumière garage allumée")
        elif valeur not in CODES_AUTORISES and valeur != "INCONNU":
            print(f"RÈGLE: code-barres refusé ({valeur}) → porte reste fermée")

    def _publier_commande(self, sujet, commande):
        self.client.publish(sujet, json.dumps({"commande": commande}))

    def demarrer(self):
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
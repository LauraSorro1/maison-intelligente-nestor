import sys
import time

from assistant.intentions import analyser, normaliser
from assistant.maison_mqtt import MaisonMQTT
from basededonnees.db import BaseDeDonnees

# TODO: définir un mot-clé pour activer l'assistant vocal (ex: "maison", "assistant", "robot", etc.)
MOT_CLE = ""

NOMS_ACTIONNEURS = {
}


class Assistant:
    def __init__(self):
        self.maison = MaisonMQTT()
        self.maison.demarrer()
        self.db = BaseDeDonnees()
    
    def executer_intention(self, intention):
        """Execute l'intention (MQTT ou lecture capteur) et construit la reponse."""
        if intention["type"] == "ACTION":
            actionneur = intention["cible"]
            action = intention["action"]

            self.maison.commander(appareil, action)

            if action == "ON":
                return f"J'allume {NOMS_ACTIONNEURS[actionneur]} du salon."
            else:
                return f"J'éteins {NOMS_ACTIONNEURS[actionneur]} du salon."

        elif intention["type"] == "REQUETE":
            capteur = intention["cible"]
            valeur = self.maison.lire(capteur)

            if valeur is None:
                return "Je n'ai pas encore reçu de lecture pour ce capteur."

            if capteur == "temperature_aquarium":
                return f"La temperature de l'aquarium est de {valeur} degrés Celsius."
            # TODO: Ajouter d'autres capteurs et leurs reponses vocales
            # elif capteur == "autre_capteur": ...

        else:
            return "Désolée, je n'ai pas compris votre demande."

    def traiter_phrase(self, phrase):
        """Analyse une phrase, execute l'intention et retourne la reponse."""
        intention = analyser(phrase)

        # TODO: Journaliser la commande recue (ou son rejet si INCONNUE) en utilisant self.db.inserer("nom_table", {"colonne": valeur, ...})
        
        reponse = self.executer_intention(intention)
        if reponse is None:
            reponse = "Désolée, je n'ai pas compris votre demande."

        # TODO: Journalise ce que l'assistant va dire a voix haute en utilisant self.db.inserer("nom_table", {"colonne": valeur, ...})
        
        return reponse

    def main(self):
        """Boucle principale : mot-cle, capture de phrase, reponse vocale."""
        from assistant.voix import Oreille, parler

        oreille = Oreille()

        parler(f"Assistant vocal démarré. Dites « {MOT_CLE} » pour m'appeler.")

        try:
            while True:
                texte = oreille.ecouter()

                if texte is None:
                    continue

                mots = normaliser(texte).split()
                mot_cle = normaliser(MOT_CLE)

                if mot_cle not in mots:
                    continue

                # Ce qui suit le mot-cle est peut-etre deja la commande :
                # « maison, allume le ventilateur » en une seule phrase.
                reste = " ".join(mots[mots.index(mot_cle) + 1:])

                if len(reste.split()) >= 2:
                    phrase = reste

                else:
                    parler("Oui, je vous écoute.")
                    phrase = oreille.ecouter(timeout=5)

                    if phrase is None:
                        parler("Je n'ai rien entendu.")
                        continue

                reponse = self.traiter_phrase(phrase)
                parler(reponse)

        except KeyboardInterrupt:
            print("\nArret de l'assistant...")

        self.arreter()

    def arreter(self):
        self.maison.arreter()
        self.db.fermer()
        print("Assistant arrete.")


if __name__ == "__main__":
    assistant = Assistant()
    assistant.main()

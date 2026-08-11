from assistant.intentions import analyser, normaliser
from assistant.maison_mqtt import MaisonMQTT
from assistant.voix import Oreille, parler
from basededonnees.db import BaseDeDonnees

# * DONE: définir un mot-clé pour activer l'assistant vocal (ex: "maison", "assistant", "robot", etc.)
# Mot-cle d'activation : « Nestor ». « Merlin » a ete abandonne — son homophone
# « merlan » est un nom commun, que le modele de langue de Google prefere
# systematiquement a un prenom rare. Nestor n'a aucun homophone, et mesure
# 5/5 au banc d'essai (test_mot_cle.py) contre 4/5 a Merlin et 3/5 a Victor.
MOT_CLE = "nestor"

# Nom officiel de l'actionneur -> nom naturel pour les reponses vocales
NOMS_ACTIONNEURS = {
    "aquarium_pompe": "la pompe de l'aquarium",
    "aquarium_uv":    "la lumière UV de l'aquarium",
    "entree_serrure": "la serrure de l'entrée",
}

# Actionneurs dont une commande doit etre confirmee avant execution.
CIBLES_A_CONFIRMER = ("entree_serrure",)

# Etat deja atteint -> phrase de constat, aucune commande publiee.
DEJA_DANS_ETAT = {
    "aquarium_pompe": {"ON": "La pompe de l'aquarium est déjà allumée.",
                       "OFF": "La pompe de l'aquarium est déjà éteinte."},
    "aquarium_uv":    {"ON": "La lumière UV de l'aquarium est déjà allumée.",
                       "OFF": "La lumière UV de l'aquarium est déjà éteinte."},
    "entree_serrure": {"ON": "La serrure de l'entrée est déjà verrouillée.",
                       "OFF": "La serrure de l'entrée est déjà déverrouillée."},
}

# Un message distinct par type d'echec de capture (seance 10).
MESSAGES_ECHEC = {
    "SILENCE":   "Je n'ai rien entendu.",
    "INCOMPRIS": "Je n'ai pas compris. Pouvez-vous répéter ?",
    "RESEAU":    "Le service de reconnaissance est indisponible pour le moment.",
}

NB_TENTATIVES = 3

# Reponses acceptees a une demande de confirmation (apres normalisation).
MOTS_OUI = ("oui", "ouais", "confirme", "vas y", "d accord")
MOTS_NON = ("non", "annule", "annuler", "laisse", "stop", "arrete")


class Assistant:
    def __init__(self):
        self.maison = MaisonMQTT()
        self.maison.demarrer()
        self.db = BaseDeDonnees()
        self.oreille = None

    def executer_intention(self, intention, phrase=""):
        """Execute l'intention (MQTT ou lecture capteur) et construit la reponse."""
        if intention["type"] == "ACTION":
            actionneur = intention["cible"]
            action = intention["action"]

            if self.maison.deja_dans_etat(actionneur, action):
                return DEJA_DANS_ETAT[actionneur][action]

            self.maison.commander(actionneur, action)   # bug corrigé : « appareil » n'existait pas

            nom = NOMS_ACTIONNEURS[actionneur]
            if actionneur == "entree_serrure":
                return f"Je verrouille {nom}." if action == "ON" else f"Je déverrouille {nom}."
            if action == "ON":
                return f"J'allume {nom}."
            return f"J'éteins {nom}."

        elif intention["type"] == "REQUETE":
            capteur = intention["cible"]
            valeur = self.maison.lire(capteur)

            if valeur is None:
                return "Je n'ai pas encore reçu de lecture pour ce capteur."

            if capteur == "temperature_aquarium":
                return f"La température de l'aquarium est de {valeur} degrés Celsius."
            # * DONE: Ajouter d'autres capteurs et leurs réponses vocales
            elif capteur == "temperature_salon":
                return f"Il fait {valeur} degrés Celsius dans le salon."

        return f"Désolé, je n'ai pas compris : {phrase}."

    def formuler_confirmation(self, intention):
        """Formule la question de confirmation d'une ACTION sensible."""
        nom = NOMS_ACTIONNEURS[intention["cible"]]
        verbe = "verrouille" if intention["action"] == "ON" else "déverrouille"
        return f"Voulez-vous que je {verbe} {nom} ? Répondez par oui ou par non."

    def demander_confirmation(self, intention):
        """Pose la question et retourne True seulement sur un oui explicite."""
        parler(self.formuler_confirmation(intention))

        for tentative in range(NB_TENTATIVES):
            reponse, echec = self.oreille.ecouter_commande()

            if echec is not None:
                parler(MESSAGES_ECHEC[echec])

                if echec == "RESEAU":
                    return False

                continue

            mots = normaliser(reponse)

            if any(mot in mots for mot in MOTS_OUI):
                return True

            if any(mot in mots for mot in MOTS_NON):
                return False

            parler("Répondez simplement par oui ou par non.")

        parler("Dans le doute, je préfère ne rien faire.")
        return False

    def obtenir_commande(self):
        """Capture une commande en NB_TENTATIVES essais. Retourne le texte ou None."""
        for tentative in range(NB_TENTATIVES):
            phrase, echec = self.oreille.ecouter_commande()

            if echec is None:
                return phrase

            parler(MESSAGES_ECHEC[echec])

            if echec == "RESEAU":
                return None

        parler("Je vous laisse. Rappelez-moi quand vous voulez.")
        return None

    def traiter_phrase(self, phrase):
        """Analyse une phrase, execute l'intention et retourne la reponse."""
        # Source de verite unique : on journalise exactement ce qui est analyse.
        phrase = normaliser(phrase)
        intention = analyser(phrase)

        # * DONE: Journaliser la commande recue (ou son rejet si INCONNUE) en utilisant self.db.inserer("nom_table", {"colonne": valeur, ...})
        self.db.inserer("journal_commandes", {
            "phrase": phrase,
            "type_intention": intention["type"],
            "cible": intention.get("cible"),
            "action": intention.get("action"),
        })

        if (intention["type"] == "ACTION"
                and intention["cible"] in CIBLES_A_CONFIRMER
                and not self.maison.deja_dans_etat(intention["cible"], intention["action"])):
            if not self.demander_confirmation(intention):
                reponse = "Très bien, je n'ai rien fait."
            else:
                reponse = self.executer_intention(intention, phrase)

        else:
            reponse = self.executer_intention(intention, phrase)

        if reponse is None:
            reponse = "Désolé, je n'ai pas compris votre demande."

        # * DONE: Journalise ce que l'assistant va dire à voix haute en utilisant self.db.inserer("nom_table", {"colonne": valeur, ...})
        self.db.inserer("journal_reponses", {
            "texte": reponse,
        })

        self.maison.publier_interaction(phrase, intention["type"], reponse)

        return reponse

    def main(self):
        """Boucle principale : mot-cle, capture de phrase, reponse vocale."""
        self.oreille = Oreille()

        parler(f"Assistant vocal démarré. Dites « {MOT_CLE} » pour m'appeler.")

        try:
            while True:
                texte = self.oreille.ecouter()

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
                    phrase = self.obtenir_commande()

                    if phrase is None:
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
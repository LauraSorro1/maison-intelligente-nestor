import os
import re
import unicodedata

import nltk

# Le tokeniseur de NLTK a besoin du modele « punkt_tab » : on le telecharge
# une seule fois (les executions suivantes le trouvent en cache local).
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

# Verbes reconnus pour interagir avec un actionneur
# (imperatif ET infinitif : « allume » / « peux-tu allumer »)
VERBES_ON = {
    "allume", "allumer", "active", "activer", "demarre", "demarrer",
    "verrouille", "verrouiller", "barre", "barrer",
}

VERBES_OFF = {
    "eteins", "eteint", "eteindre", "ferme", "fermer", "arrete", "arreter",
    "desactive", "desactiver", "deverrouille", "deverrouiller", "debarre", "debarrer",
}

# Noms d'actionneurs (et leurs surnoms) -> nom officiel de l'actionneur
ACTIONNEURS = {
    "pompe": "aquarium_pompe",
    "uv": "aquarium_uv",
    "sterilisateur": "aquarium_uv",
    "serrure": "entree_serrure",
    "porte": "entree_serrure",
    "verrou": "entree_serrure",
}

# Mots-cles qui indiquent une requete d'etat -> nom officiel du capteur
CAPTEURS = {
    "aquarium": "temperature_aquarium",
    "salon": "temperature_salon",
}

# * DONE: Ajouter un regex pour detecter les formules de politesse (bonjour, merci, s'il vous plait, etc.)
# Formules de politesse à retirer avant l'analyse (elles ne changent pas l'intention).
# Ecrites sans accents et avec espaces (appliquees APRES normalisation des accents
# et des apostrophes : « s'il te plaît » est deja devenu « s il te plait »).
POLITESSE = re.compile(
    r"\b(bonjour|salut|merci|s il te plait|s il vous plait|stp|svp|je voudrais|peux tu|pouvez vous)\b"
)


# * DONE: Normaliser la phrase (minuscules, accents, ponctuation, politesse)
def normaliser(phrase):
    """Prepare une phrase pour l'analyse : minuscules, sans accents,
    sans ponctuation ni formules de politesse."""
    texte = phrase.lower()                                      # 1. minuscules
    texte = unicodedata.normalize("NFD", texte)                 # 2. decompose e+accent
    texte = "".join(c for c in texte if not unicodedata.combining(c))  # jette les accents
    texte = texte.replace("'", " ").replace("-", " ")           # 3. apostrophes et tirets
    texte = POLITESSE.sub(" ", texte)                           # 4. retire la politesse
    texte = re.sub(r"[^a-z0-9 ]", " ", texte)                   # 5. ponctuation restante
    texte = re.sub(r"\s+", " ", texte).strip()                  # espaces multiples
    return texte
    

# * DONE: Ajouter la tokenisation avec NLTK
def tokeniser(texte):
    """Decoupe le texte normalise en jetons (mots) avec NLTK."""
    return nltk.word_tokenize(texte, language="french")


def trouver_action(tokens):
    """Cherche un verbe d'action (ON ou OFF) dans la phrase."""
    for token in tokens:
        if token in VERBES_ON:
            return "ON"
        if token in VERBES_OFF:
            return "OFF"
    return None


def analyser(phrase):
    """Transforme une phrase libre en intention structuree.

    Retourne un dictionnaire :
        type   : "ACTION", "REQUETE" ou "INCONNUE"
        cible  : nom de l'actionneur ou du capteur vise
        action : "ON" / "OFF" pour une ACTION, sinon None
    """
    texte = normaliser(phrase)
    tokens = tokeniser(texte)

    action = trouver_action(tokens)

    actionneur = None
    capteur = None
    for token in tokens:
        if actionneur is None and token in ACTIONNEURS:
            actionneur = ACTIONNEURS[token]
        if capteur is None and token in CAPTEURS:
            capteur = CAPTEURS[token]

    if action and actionneur:
        return {
            "type": "ACTION", 
            "cible": actionneur, 
            "action": action}

    if capteur and not action:
        return {
            "type": "REQUETE", 
            "cible": capteur, 
            "action": None}

    return {
        "type": "INCONNUE", 
        "cible": None, 
        "action": None}

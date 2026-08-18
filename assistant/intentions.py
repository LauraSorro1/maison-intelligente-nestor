import re
import unicodedata

import nltk
from nltk.stem import SnowballStemmer

# Le tokeniseur de NLTK a besoin du modele « punkt_tab » : on le telecharge
# une seule fois (les executions suivantes le trouvent en cache local).
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

# Racines des verbes reconnus (seance 12 : SnowballStemmer).
# Une racine couvre toutes les formes regulieres d'un meme verbe :
# racine.stem("allume") = racine.stem("allumez") = racine.stem("allumer") = "allum".
# Les verbes irreguliers (eteindre) donnent plusieurs racines : elles sont
# toutes listees, une par forme reellement prononcable.
RACINES_ON = {
    "allum",        # allume, allumes, allumez, allumer, allume
    "activ",        # active, actives, activez, activer
    "demarr",       # demarre, demarres, demarrez, demarrer
    "met",          # mets, met  (« mets la pompe en marche »)
    "verrouill",    # verrouille, verrouillez, verrouiller
    "barr",         # barre, barrez, barrer
}

RACINES_OFF = {
    "etein", "eteint", "eteindr", "eteign",   # eteins / eteint / eteindre / eteignez
    "ferm",         # ferme, fermez, fermer
    "arret",        # arrete, arretez, arreter
    "desact", "desactiv",                     # desactive / desactiver
    "deverrouill",  # deverrouille, deverrouillez, deverrouiller
    "debarr",       # debarre, debarrez, debarrer
    "coup",         # coupe, coupez, couper
    "stopp",        # stoppe, stoppez, stopper
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


# Le stemmer francais est purement algorithmique : aucun telechargement.
_racine = SnowballStemmer("french")


def trouver_action(tokens):
    """Cherche un verbe d'action (ON ou OFF) parmi les jetons, par leur racine."""
    for token in tokens:
        r = _racine.stem(token)
        if r in RACINES_ON:
            return "ON"
        if r in RACINES_OFF:
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
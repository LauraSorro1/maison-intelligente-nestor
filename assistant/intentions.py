import os
import re
import unicodedata

import nltk


# Verbes reconnus pour interagir avec un actionneur
VERBES_ON = {
}

VERBES_OFF = {
}

# Noms d'actionneurs (et leurs surnoms) -> nom officiel de l'actionneur
ACTIONNEURS = {
}

# Mots-cles qui indiquent une requete d'etat -> nom officiel du capteur
CAPTEURS = {
    "temperature": "temperature_aquarium",
}

# TODO: Ajouter un regex pour detecter les formules de politesse (bonjour, merci, s'il vous plait, etc.)
POLITESSE = re.compile(r"")

# TODO: Normaliser la phrase (minuscules, accents, ponctuation, politesse)
def normaliser(phrase):
    pass
    

# TODO: Ajouter la tokenisation avec NLTK
def tokeniser(texte):
    pass


def trouver_action(texte, tokens):
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

    action = trouver_action(texte, tokens)

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

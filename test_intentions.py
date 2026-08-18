"""Petit banc d'essai pour l'analyse des intentions (usage local, pas remis)."""
from assistant.intentions import normaliser, tokeniser, analyser

phrases = [
    "Nestor, allume la Pompe de l'aquarium s'il te plaît !",
    "Éteins la lumière UV, merci.",
    "Peux-tu verrouiller la porte d'entrée ?",
    "Quelle température fait-il dans le salon ?",
    "Quelle est la température de l'aquarium ?",
    "Fais-moi un café",  # doit donner INCONNUE
]

for p in phrases:
    print(f"{p!r}")
    print(f"   -> {analyser(p)}\n")
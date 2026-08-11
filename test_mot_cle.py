"""Banc d'essai des mots-cles candidats.

Usage : py -3.13 test_mot_cle.py
Prononcer chaque candidat 5 fois, puis comparer les taux de reconnaissance.
"""

from assistant.intentions import normaliser
from assistant.voix import Oreille

CANDIDATS = ["victor", "athena", "nestor", "merlin"]
ESSAIS = 5


def main():
    oreille = Oreille()
    resultats = {}

    for candidat in CANDIDATS:
        print(f"\n=== {candidat.upper()} — {ESSAIS} essais ===")
        reussites = 0

        for essai in range(1, ESSAIS + 1):
            print(f"  Essai {essai}/{ESSAIS} — prononcez « {candidat} » seul...")
            texte = oreille.ecouter(timeout=8, limite=3)

            if texte is None:
                print("    -> rien capte")
                continue

            mots = normaliser(texte).split()

            if candidat in mots:
                reussites += 1
                print(f"    -> OK  ({texte})")
            else:
                print(f"    -> RATE ({texte})")

        resultats[candidat] = reussites

    print("\n=== RESULTATS ===")
    for candidat, reussites in sorted(resultats.items(), key=lambda x: -x[1]):
        print(f"{candidat:<10} {reussites}/{ESSAIS}")


if __name__ == "__main__":
    main()
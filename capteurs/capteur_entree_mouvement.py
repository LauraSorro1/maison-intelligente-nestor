"""Capteur de mouvement de l'entrée — classe Python.

Publie 0 ou 1 sur maison/entree/mouvement.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_entree_mouvement
"""
import random
from config import SujetsCapteurs
from capteurs.base_capteur import Capteur


class CapteurEntreeMouvement(Capteur):
    def __init__(self):
        super().__init__(
            type_capteur="mouvement_entree",
            sujet=SujetsCapteurs.ENTREE_MOUVEMENT,
            unite="",
            periode=1.0,
            client=Capteur.creer_client(
                "capteur-entree-mouvement",
                "maison/entree/mouvement/sante"
            )
        )
        self.valeur = 0  # pas de mouvement au départ

    def lire(self):
        # Simule une détection : 20% de chance que l'état change
        if random.random() < 0.2:
            self.valeur = 1 if self.valeur == 0 else 0
        return self.valeur


if __name__ == "__main__":
    CapteurEntreeMouvement().demarrer()
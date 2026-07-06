"""Capteur de mouvement de l'entrée — OpenCV — classe Python.

Détecte le mouvement via la webcam et publie 0 ou 1
sur maison/entree/mouvement.

Lancer comme module, depuis le dossier projet1-420-315-E26/ :
    python -m capteurs.capteur_entree_mouvement
"""
import cv2
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
        self.valeur = 0
        self.cap = cv2.VideoCapture(0)      # webcam intégrée
        self.frame_precedente = None         # frame de référence

    def lire(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Erreur : impossible de lire la webcam.")
            return self.valeur
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # conversion en niveaux de gris
        gris = cv2.GaussianBlur(gris, (21, 21), 0)  # flou pour réduire le bruit
        self.frame_precedente = self.frame_precedente if self.frame_precedente is not None else gris
        diff = cv2.absdiff(self.frame_precedente, gris)  # différence entre frames
        _, seuil = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)  # seuillage
        self.valeur = 1 if seuil.sum() > 10000 else 0  # seuil pour détecter le mouvement
        self.frame_precedente = gris  # mise à jour de la frame précédente
        return self.valeur

    def __del__(self):
        self.cap.release()


if __name__ == "__main__":
    CapteurEntreeMouvement().demarrer()
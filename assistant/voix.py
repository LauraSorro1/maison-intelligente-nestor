import pyttsx3
import speech_recognition as sr

# * DONE: Ajouter la lecture du texte a voix haute avec pyttsx3 en Francais

# Moteur initialisé UNE SEULE FOIS au chargement du module (init() est lent ~1s).
# Voix ciblée : Microsoft Claude (français canadien). Si absente sur la machine,
# on retombe sur la première voix française trouvée.
_moteur = pyttsx3.init()
_voix_francaise = None
for _voix in _moteur.getProperty('voices'):
    if "Claude" in _voix.name:              # voix préférée : Claude (fr-CA)
        _voix_francaise = _voix.id
        break
    if _voix_francaise is None and "fr" in _voix.id.lower():
        _voix_francaise = _voix.id          # plan B : première voix française
if _voix_francaise:
    _moteur.setProperty('voice', _voix_francaise)


def parler(texte):
    """Lit le texte a voix haute avec une voix francaise si disponible."""
    print(f"Assistant : {texte}")
    _moteur.say(texte)
    _moteur.runAndWait()


class Oreille:
    """Capture la voix au micro et la transforme en texte."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Tolerance aux pauses naturelles : on attend 1,5 s de silence avant
        # de considerer la phrase terminee (defaut 0,8 s — coupait les phrases).
        self.recognizer.pause_threshold = 1.5
        # Seuil fige apres calibration : sinon il se reajuste PENDANT la phrase
        # et coupe la fin quand la voix baisse.
        self.recognizer.dynamic_energy_threshold = False
        self.micro = sr.Microphone()

        print("Calibration du micro (silence pendant 2 secondes)...")

        with self.micro as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)

    def _capter(self, timeout, limite):
        """Capture unique. Retourne (texte, echec).

        echec vaut None en cas de succes, sinon "SILENCE", "INCOMPRIS"
        ou "RESEAU". Cette fonction ne parle jamais : l'appelant decide.
        """
        try:
            with self.micro as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=limite
                )

        except sr.WaitTimeoutError:
            return None, "SILENCE"

        try:
            texte = self.recognizer.recognize_google(audio, language="fr-FR")
            print(f"Entendu : {texte}")
            return texte, None

        except sr.UnknownValueError:
            return None, "INCOMPRIS"

        except sr.RequestError as erreur:
            print(f"Erreur du service de reconnaissance : {erreur}")
            return None, "RESEAU"

    def ecouter(self, timeout=5, limite=8):
        """Veille du mot-cle : retourne le texte reconnu, ou None."""
        texte, _ = self._capter(timeout, limite)
        return texte

    def ecouter_commande(self, timeout=5, limite=8):
        """Capture d'une commande : retourne (texte, echec)."""
        return self._capter(timeout, limite)
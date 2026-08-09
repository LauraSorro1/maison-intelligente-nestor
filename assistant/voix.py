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
        # Tolerance aux pauses naturelles : on attend 1,2 s de silence avant
        # de considerer la phrase terminee (defaut 0,8 s — coupait les phrases).
        self.recognizer.pause_threshold = 1.2
        self.micro = sr.Microphone()

        print("Calibration du micro (silence pendant 1 seconde)...")

        with self.micro as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def ecouter(self, timeout=None, limite=8):
        """Ecoute une phrase et retourne le texte reconnu (ou None)."""
        try:
            with self.micro as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=limite
                )

        except sr.WaitTimeoutError:
            return None

        try:
            texte = self.recognizer.recognize_google(audio, language="fr-FR")
            print(f"Entendu : {texte}")
            return texte

        except sr.UnknownValueError:
            return None

        except sr.RequestError as erreur:
            print(f"Erreur du service de reconnaissance : {erreur}")
            return None

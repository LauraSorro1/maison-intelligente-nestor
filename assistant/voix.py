import pyttsx3
import speech_recognition as sr

# TODO: Ajouter la lecture du texte a voix haute avec pyttsx3 en Francais
def parler(texte):
    """Lit le texte a voix haute avec une voix francaise si disponible."""
    print(f"Assistant : {texte}")
    pass


class Oreille:
    """Capture la voix au micro et la transforme en texte."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
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

# services/benutzer_service.py

from typing import Optional

from datenbank.benutzer_repository import BenutzerRepository
from modelle.benutzer import Benutzer
from sicherheit.passwort_hasher import hash_passwort


class BenutzerService:
    
    # Enthält die Logik rund um Registrierung und Anmeldung.
    # Der Service spricht mit dem Repository und kümmert sich um das Hashen des Passworts.
    

    def __init__(self):
        self.benutzer_repository = BenutzerRepository()

    def registriere_neuen_benutzer(self, email: str, passwort: str) -> bool:
        
        # Versucht, einen neuen Benutzer anzulegen.
        # Gibt True zurück, wenn es geklappt hat.
        
        if not email or not passwort:
            print("E-Mail und Passwort dürfen nicht leer sein.")
            return False

        passwort_hash = hash_passwort(passwort)
        erfolgreich = self.benutzer_repository.registriere_benutzer(
            email=email, passwort_hash=passwort_hash
        )

        if erfolgreich:
            print("Benutzer wurde erfolgreich registriert.")
        else:
            print(
                "Registrierung fehlgeschlagen. "
                "Vielleicht existiert die E-Mail bereits?"
            )

        return erfolgreich

    def melde_benutzer_an(self, email: str, passwort: str) -> Optional[Benutzer]:
        
        # Prüft E-Mail und Passwort.
        # Gibt ein Benutzer-Objekt zurück, wenn die Anmeldung erfolgreich war.
        
        gespeicherter_hash = self.benutzer_repository.hole_passwort_hash(email)

        if gespeicherter_hash is None:
            print("Kein Benutzer mit dieser E-Mail gefunden.")
            return None

        eingegebener_hash = hash_passwort(passwort)

        if eingegebener_hash != gespeicherter_hash:
            print("Passwort ist falsch.")
            return None

        benutzer = self.benutzer_repository.finde_benutzer_nach_email(email)
        return benutzer
